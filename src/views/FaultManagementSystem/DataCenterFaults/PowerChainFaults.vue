<script setup lang="ts">
import { ref, onMounted, nextTick, watch, onUnmounted, computed } from 'vue'
import {
  Search, RefreshRight, Warning, CircleCheck, Clock,
  TrendCharts, Monitor, Connection, DataAnalysis,
  Document, Setting, More, ArrowUp, ArrowDown,
  VideoCamera, Histogram, Lightning, Link
} from "@element-plus/icons-vue"
import * as echarts from 'echarts'
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Connecting to power distribution system...',
  'Loading power chain topology...',
  'Analyzing power quality...'
]

// Power Chain Components Data
const powerComponents = ref([
  {
    id: 'SWGR-MAIN-01',
    name: 'Main Switchgear',
    location: 'Data Center A - Electrical Room',
    type: 'Switchgear',
    status: 'healthy',
    voltage: 13800,
    current: 1250,
    power: 17250,
    frequency: 60.02,
    temperature: 32,
    alerts: [],
    lastMaintenance: '2024-12-01',
    nextMaintenance: '2025-03-01'
  },
  {
    id: 'TX-01-DC-A',
    name: 'Main Transformer 1',
    location: 'Data Center A - Transformer Yard',
    type: 'Transformer',
    status: 'warning',
    voltage: 13800,
    secondaryVoltage: 480,
    current: 1150,
    power: 15800,
    temperature: 78,
    oilTemp: 72,
    loadPercent: 82,
    alerts: [
      { severity: 'warning', message: 'Transformer temperature above normal range', timestamp: '2025-01-16 08:30:00' },
      { severity: 'info', message: 'Load approaching 85% capacity', timestamp: '2025-01-15 14:20:00' }
    ],
    lastMaintenance: '2024-11-15',
    nextMaintenance: '2025-02-15'
  },
  {
    id: 'GEN-01-DC-A',
    name: 'Emergency Generator 1',
    location: 'Data Center A - Generator Room',
    type: 'Generator',
    status: 'healthy',
    voltage: 480,
    current: 850,
    power: 680,
    fuelLevel: 92,
    runtime: 1245,
    lastTest: '2025-01-15',
    alerts: [],
    lastMaintenance: '2025-01-05',
    nextMaintenance: '2025-04-05'
  },
  {
    id: 'GEN-02-DC-A',
    name: 'Emergency Generator 2',
    location: 'Data Center A - Generator Room',
    type: 'Generator',
    status: 'warning',
    voltage: 478,
    current: 820,
    power: 655,
    fuelLevel: 88,
    runtime: 1180,
    lastTest: '2025-01-08',
    alerts: [
      { severity: 'warning', message: 'Generator not tested in 7 days', timestamp: '2025-01-15 09:00:00' }
    ],
    lastMaintenance: '2024-12-20',
    nextMaintenance: '2025-03-20'
  },
  {
    id: 'ATS-01-DC-A',
    name: 'Automatic Transfer Switch 1',
    location: 'Data Center A - Electrical Room',
    type: 'ATS',
    status: 'healthy',
    source: 'Utility',
    utilityVoltage: 480,
    generatorVoltage: 478,
    transferTime: 2.5,
    alerts: [],
    lastMaintenance: '2024-12-10',
    nextMaintenance: '2025-03-10'
  },
  {
    id: 'UPS-01-DC-A',
    name: 'UPS Main 1',
    location: 'Data Center A - UPS Room',
    type: 'UPS',
    status: 'critical',
    inputVoltage: 480,
    outputVoltage: 478,
    loadPercent: 88,
    batteryCharge: 76,
    efficiency: 92.5,
    bypass: false,
    alerts: [
      { severity: 'critical', message: 'UPS overload - load exceeds 85%', timestamp: '2025-01-16 10:15:00' },
      { severity: 'warning', message: 'Battery health degrading', timestamp: '2025-01-14 09:45:00' }
    ],
    lastMaintenance: '2024-10-15',
    nextMaintenance: '2025-01-15'
  },
  {
    id: 'PDU-01-R1',
    name: 'Power Distribution Unit Row 1',
    location: 'Data Center A - Row 1',
    type: 'PDU',
    status: 'healthy',
    voltage: 415,
    current: 320,
    power: 220,
    phaseBalance: 2.5,
    alerts: [],
    lastMaintenance: '2024-12-28',
    nextMaintenance: '2025-03-28'
  },
  {
    id: 'PDU-02-R2',
    name: 'Power Distribution Unit Row 2',
    location: 'Data Center A - Row 2',
    type: 'PDU',
    status: 'warning',
    voltage: 412,
    current: 380,
    power: 260,
    phaseBalance: 5.8,
    alerts: [
      { severity: 'warning', message: 'Phase imbalance detected', timestamp: '2025-01-15 13:30:00' }
    ],
    lastMaintenance: '2024-12-20',
    nextMaintenance: '2025-03-20'
  }
])

// Power Chain Topology
const powerChainTopology = ref([
  { level: 0, name: 'Utility Feed', status: 'healthy', components: ['Utility Grid'] },
  { level: 1, name: 'Main Switchgear', status: 'healthy', components: ['SWGR-MAIN-01'] },
  { level: 2, name: 'Transformers', status: 'warning', components: ['TX-01-DC-A'] },
  { level: 3, name: 'Generators', status: 'warning', components: ['GEN-01-DC-A', 'GEN-02-DC-A'] },
  { level: 4, name: 'ATS', status: 'healthy', components: ['ATS-01-DC-A'] },
  { level: 5, name: 'UPS Systems', status: 'critical', components: ['UPS-01-DC-A'] },
  { level: 6, name: 'PDUs', status: 'warning', components: ['PDU-01-R1', 'PDU-02-R2'] },
  { level: 7, name: 'IT Loads', status: 'healthy', components: ['Servers', 'Storage', 'Network'] }
])

// Historical fault data
const faultHistory = ref([
  { id: 'PFLT-001', componentId: 'UPS-01-DC-A', type: 'Overload', severity: 'critical', timestamp: '2025-01-16 10:15:00', resolved: '', description: 'UPS load exceeded 85% capacity' },
  { id: 'PFLT-002', componentId: 'TX-01-DC-A', type: 'High Temperature', severity: 'warning', timestamp: '2025-01-15 08:30:00', resolved: '2025-01-15 11:20:00', description: 'Transformer temperature reached 78°C' },
  { id: 'PFLT-003', componentId: 'PDU-02-R2', type: 'Phase Imbalance', severity: 'warning', timestamp: '2025-01-14 14:45:00', resolved: '2025-01-14 16:30:00', description: 'Phase imbalance exceeded 5%' },
  { id: 'PFLT-004', componentId: 'GEN-02-DC-A', type: 'Test Missed', severity: 'warning', timestamp: '2025-01-13 09:00:00', resolved: '', description: 'Weekly generator test not performed' }
])

// Power quality data
const powerQualityData = ref([
  { time: '00:00', voltage: 480, current: 850, pf: 0.95, thd: 2.1 },
  { time: '02:00', voltage: 481, current: 820, pf: 0.96, thd: 2.0 },
  { time: '04:00', voltage: 480, current: 780, pf: 0.96, thd: 1.9 },
  { time: '06:00', voltage: 479, current: 800, pf: 0.95, thd: 2.0 },
  { time: '08:00', voltage: 480, current: 950, pf: 0.94, thd: 2.3 },
  { time: '10:00', voltage: 478, current: 1050, pf: 0.93, thd: 2.5 },
  { time: '12:00', voltage: 479, current: 1080, pf: 0.93, thd: 2.6 },
  { time: '14:00', voltage: 477, current: 1120, pf: 0.92, thd: 2.8 },
  { time: '16:00', voltage: 478, current: 1060, pf: 0.93, thd: 2.7 },
  { time: '18:00', voltage: 479, current: 980, pf: 0.94, thd: 2.4 },
  { time: '20:00', voltage: 480, current: 920, pf: 0.95, thd: 2.2 },
  { time: '22:00', voltage: 480, current: 880, pf: 0.95, thd: 2.1 }
])

// Load distribution
const loadDistribution = ref([
  { component: 'IT Equipment', load: 1250, percentage: 62 },
  { component: 'Cooling', load: 450, percentage: 22 },
  { component: 'Lighting', load: 120, percentage: 6 },
  { component: 'UPS Losses', load: 100, percentage: 5 },
  { component: 'Other', load: 100, percentage: 5 }
])

// Selected component
const selectedComponent = ref<any>(null)
const detailVisible = ref(false)
const historyVisible = ref(false)
const topologyVisible = ref(false)

// Filters
const searchKeyword = ref('')
const statusFilter = ref('all')
const typeFilter = ref('all')
const currentPage = ref(1)
const pageSize = ref(10)

// Chart refs
const powerQualityChartRef = ref<HTMLElement | null>(null)
const loadChartRef = ref<HTMLElement | null>(null)
let powerQualityChart: echarts.ECharts | null = null
let loadChart: echarts.ECharts | null = null

const filteredComponents = computed(() => {
  let filtered = powerComponents.value

  if (statusFilter.value !== 'all') {
    filtered = filtered.filter(c => c.status === statusFilter.value)
  }

  if (typeFilter.value !== 'all') {
    filtered = filtered.filter(c => c.type === typeFilter.value)
  }

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(c =>
        c.id.toLowerCase().includes(keyword) ||
        c.name.toLowerCase().includes(keyword) ||
        c.location.toLowerCase().includes(keyword)
    )
  }

  return filtered
})

const paginatedComponents = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredComponents.value.slice(start, end)
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

const getChainStatusColor = (status: string) => {
  switch(status) {
    case 'critical': return '#F56C6C'
    case 'warning': return '#E6A23C'
    case 'healthy': return '#67C23A'
    default: return '#909399'
  }
}

const viewDetails = (component: any) => {
  selectedComponent.value = component
  detailVisible.value = true
}

const viewHistory = (component: any) => {
  selectedComponent.value = component
  historyVisible.value = true
}

const viewTopology = () => {
  topologyVisible.value = true
}

const performTransfer = (component: any) => {
  ElMessageBox.confirm(
      `Initiate transfer for ${component.id}? This will switch power sources.`,
      'Confirm Transfer',
      {
        confirmButtonText: 'Transfer',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  ).then(() => {
    ElMessage.success(`Transfer initiated for ${component.id}`)
  }).catch(() => {})
}

const scheduleMaintenance = (component: any) => {
  ElMessageBox.confirm(
      `Schedule maintenance for ${component.id}?`,
      'Schedule Maintenance',
      {
        confirmButtonText: 'Schedule',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  ).then(() => {
    ElMessage.success(`Maintenance scheduled for ${component.id}`)
  }).catch(() => {})
}

const clearAlerts = (component: any) => {
  component.alerts = []
  ElMessage.success(`Alerts cleared for ${component.id}`)
}

const refreshData = () => {
  ElMessage.info('Refreshing power chain data...')
  setTimeout(() => {
    ElMessage.success('Data refreshed successfully')
  }, 1000)
}

const initPowerQualityChart = () => {
  if (powerQualityChartRef.value) {
    if (powerQualityChart) powerQualityChart.dispose()

    powerQualityChart = echarts.init(powerQualityChartRef.value)
    powerQualityChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: {
        data: ['Voltage (V)', 'Current (A)', 'Power Factor', 'THD (%)'],
        left: 'left',
        textStyle: { color: '#606266' }
      },
      grid: { left: '8%', right: '8%', top: '15%', bottom: '8%', containLabel: true },
      xAxis: {
        type: 'category',
        data: powerQualityData.value.map(d => d.time),
        axisLabel: { rotate: 45 }
      },
      yAxis: [
        { type: 'value', name: 'Voltage (V)', min: 450, max: 510 },
        { type: 'value', name: 'Current (A)', min: 500, max: 1300 },
        { type: 'value', name: 'PF / THD (%)', min: 0, max: 10 }
      ],
      series: [
        {
          name: 'Voltage (V)',
          type: 'line',
          data: powerQualityData.value.map(d => d.voltage),
          smooth: true,
          lineStyle: { color: '#409EFF', width: 3 },
          symbol: 'circle',
          symbolSize: 6,
          label: { show: true, position: 'top', formatter: '{c}V' }
        },
        {
          name: 'Current (A)',
          type: 'line',
          data: powerQualityData.value.map(d => d.current),
          smooth: true,
          lineStyle: { color: '#F56C6C', width: 3 },
          symbol: 'diamond',
          symbolSize: 6,
          label: { show: true, position: 'top', formatter: '{c}A' }
        },
        {
          name: 'Power Factor',
          type: 'line',
          yAxisIndex: 2,
          data: powerQualityData.value.map(d => d.pf),
          smooth: true,
          lineStyle: { color: '#67C23A', width: 2 },
          symbol: 'triangle',
          symbolSize: 6
        },
        {
          name: 'THD (%)',
          type: 'line',
          yAxisIndex: 2,
          data: powerQualityData.value.map(d => d.thd),
          smooth: true,
          lineStyle: { color: '#E6A23C', width: 2, type: 'dashed' },
          symbol: 'square',
          symbolSize: 6
        }
      ]
    })
  }
}

const initLoadChart = () => {
  if (loadChartRef.value) {
    if (loadChart) loadChart.dispose()

    loadChart = echarts.init(loadChartRef.value)
    loadChart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c} kW)' },
      legend: {
        orient: 'vertical',
        left: 'left',
        textStyle: { color: '#606266' }
      },
      series: [
        {
          name: 'Load Distribution',
          type: 'pie',
          radius: ['40%', '65%'],
          data: loadDistribution.value.map(l => ({ name: l.component, value: l.load })),
          label: { show: true, formatter: '{b}: {d}%' },
          emphasis: { scale: true },
          itemStyle: {
            borderRadius: 8,
            borderColor: '#fff',
            borderWidth: 2
          }
        }
      ]
    })
  }
}

const handleResize = () => {
  powerQualityChart?.resize()
  loadChart?.resize()
}

watch(isLoaded, (loaded) => {
  if (loaded) {
    nextTick(() => {
      initPowerQualityChart()
      initLoadChart()
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
  powerQualityChart?.dispose()
  loadChart?.dispose()
})

// Helper computed values
const totalLoad = computed(() => {
  return loadDistribution.value.reduce((sum, l) => sum + l.load, 0)
})

const criticalCount = computed(() => {
  return powerComponents.value.filter(c => c.status === 'critical').length
})

const warningCount = computed(() => {
  return powerComponents.value.filter(c => c.status === 'warning').length
})

const healthyCount = computed(() => {
  return powerComponents.value.filter(c => c.status === 'healthy').length
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
        <div class="loading-tip">Power Chain Fault Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="power-chain-faults">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Power Chain Fault Management</h2>
        <p class="subtitle">End-to-end power distribution monitoring and fault analysis</p>
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
        <el-select v-model="typeFilter" placeholder="Type" clearable style="width: 140px">
          <el-option label="All" value="all" />
          <el-option label="Switchgear" value="Switchgear" />
          <el-option label="Transformer" value="Transformer" />
          <el-option label="Generator" value="Generator" />
          <el-option label="ATS" value="ATS" />
          <el-option label="UPS" value="UPS" />
          <el-option label="PDU" value="PDU" />
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
            <div class="stat-value">{{ powerComponents.length }}</div>
            <div class="stat-label">Total Components</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon healthy">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ healthyCount }}</div>
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
            <div class="stat-value">{{ warningCount }}</div>
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
            <div class="stat-value">{{ criticalCount }}</div>
            <div class="stat-label">Critical</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon load">
            <el-icon><Lightning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ totalLoad }} kW</div>
            <div class="stat-label">Total Load</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Power Chain Topology -->
    <div class="topology-summary">
      <div class="topology-header">
        <span>Power Chain Topology</span>
        <el-button type="primary" link @click="viewTopology">
          <el-icon><Link /></el-icon> View Full Topology
        </el-button>
      </div>
      <div class="chain-visualization">
        <div v-for="(level, index) in powerChainTopology" :key="index" class="chain-level">
          <div class="level-line"></div>
          <div class="level-content" :class="level.status">
            <div class="level-name">{{ level.name }}</div>
            <div class="level-status" :style="{ color: getChainStatusColor(level.status) }">
              {{ level.status.toUpperCase() }}
            </div>
            <div class="level-components">{{ level.components.join(', ') }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>Power Quality Trends (24 Hours)</span>
            <el-tag type="info" size="small">Real-time</el-tag>
          </div>
        </template>
        <div ref="powerQualityChartRef" class="chart"></div>
      </el-card>

      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>Load Distribution</span>
            <el-tag type="success" size="small">By Category</el-tag>
          </div>
        </template>
        <div ref="loadChartRef" class="chart"></div>
      </el-card>
    </div>

    <!-- Power Components Table -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="table-header">
          <span class="table-title">Power Chain Components</span>
          <span class="table-subtitle">{{ filteredComponents.length }} components displayed</span>
        </div>
      </template>
      <el-table :data="paginatedComponents" stripe style="width: 100%">
        <el-table-column prop="id" label="Component ID" width="140" align="center"  />
        <el-table-column prop="name" label="Name" min-width="160" align="center"  />
        <el-table-column prop="location" label="Location" min-width="200"  align="center"  show-overflow-tooltip />
        <el-table-column prop="type" label="Type"  align="center"  />
        <el-table-column label="Status" align="center" >
          <template #default="{ row }">
            <div class="status-indicator">
              <span class="status-dot" :style="{ background: getStatusColor(row.status) }"></span>
              <span>{{ getStatusText(row.status) }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Load" align="center" >
          <template #default="{ row }">
            <span v-if="row.loadPercent">{{ row.loadPercent }}%</span>
            <span v-else-if="row.power">{{ row.power }} kW</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="Voltage" align="center" >
          <template #default="{ row }">
            <span v-if="row.voltage">{{ row.voltage }}V</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="Current" align="center" >
          <template #default="{ row }">
            <span v-if="row.current">{{ row.current }}A</span>
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
        <el-table-column label="Actions" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewDetails(row)">Details</el-button>
            <el-button type="info" link size="small" @click="viewHistory(row)">History</el-button>
            <el-button type="warning" link size="small" @click="performTransfer(row)" v-if="row.type === 'ATS'">Transfer</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredComponents.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Component Detail Dialog -->
    <el-dialog v-model="detailVisible" :title="selectedComponent?.name" width="750px">
      <div v-if="selectedComponent" class="component-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Component ID">{{ selectedComponent.id }}</el-descriptions-item>
          <el-descriptions-item label="Type">{{ selectedComponent.type }}</el-descriptions-item>
          <el-descriptions-item label="Location">{{ selectedComponent.location }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <span class="status-indicator">
              <span class="status-dot" :style="{ background: getStatusColor(selectedComponent.status) }"></span>
              {{ getStatusText(selectedComponent.status) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="Last Maintenance">{{ selectedComponent.lastMaintenance }}</el-descriptions-item>
          <el-descriptions-item label="Next Maintenance">{{ selectedComponent.nextMaintenance }}</el-descriptions-item>
          <el-descriptions-item v-if="selectedComponent.voltage" label="Voltage">{{ selectedComponent.voltage }}V</el-descriptions-item>
          <el-descriptions-item v-if="selectedComponent.current" label="Current">{{ selectedComponent.current }}A</el-descriptions-item>
          <el-descriptions-item v-if="selectedComponent.power" label="Power">{{ selectedComponent.power }} kW</el-descriptions-item>
          <el-descriptions-item v-if="selectedComponent.loadPercent" label="Load">{{ selectedComponent.loadPercent }}%</el-descriptions-item>
          <el-descriptions-item v-if="selectedComponent.temperature" label="Temperature">{{ selectedComponent.temperature }}°C</el-descriptions-item>
          <el-descriptions-item v-if="selectedComponent.fuelLevel" label="Fuel Level">{{ selectedComponent.fuelLevel }}%</el-descriptions-item>
          <el-descriptions-item v-if="selectedComponent.batteryCharge" label="Battery Charge">{{ selectedComponent.batteryCharge }}%</el-descriptions-item>
          <el-descriptions-item v-if="selectedComponent.efficiency" label="Efficiency">{{ selectedComponent.efficiency }}%</el-descriptions-item>
        </el-descriptions>

        <div v-if="selectedComponent.alerts.length > 0" class="alerts-section">
          <h4>Active Alerts</h4>
          <el-table :data="selectedComponent.alerts" size="small">
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
            <el-button type="primary" size="small" @click="clearAlerts(selectedComponent)">Clear Alerts</el-button>
          </div>
        </div>

        <div class="detail-actions">
          <el-button type="warning" @click="scheduleMaintenance(selectedComponent)">Schedule Maintenance</el-button>
          <el-button type="primary" @click="viewHistory(selectedComponent)">View Fault History</el-button>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Topology Dialog -->
    <el-dialog v-model="topologyVisible" title="Power Chain Topology Diagram" width="900px">
      <div class="topology-diagram">
        <div v-for="(level, index) in powerChainTopology" :key="index" class="topology-level">
          <div class="topology-level-name">{{ level.name }}</div>
          <div class="topology-components">
            <div v-for="comp in level.components" :key="comp" class="topology-component" :class="level.status">
              <div class="comp-name">{{ comp }}</div>
              <div class="comp-status" :style="{ color: getChainStatusColor(level.status) }">
                {{ level.status.toUpperCase() }}
              </div>
            </div>
          </div>
          <div v-if="index < powerChainTopology.length - 1" class="topology-arrow">↓</div>
        </div>
      </div>
      <template #footer>
        <el-button @click="topologyVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Fault History Dialog -->
    <el-dialog v-model="historyVisible" :title="`Fault History - ${selectedComponent?.id}`" width="800px">
      <el-table :data="faultHistory.filter(f => f.componentId === selectedComponent?.id)" stripe>
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
.power-chain-faults {
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
.stat-icon.load { background: rgba(230, 162, 60, 0.1); color: #E6A23C; }

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

/* Topology Summary */
.topology-summary {
  background: white;
  border-radius: 16px;
  padding: 16px 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.topology-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  font-weight: 600;
  font-size: 15px;
}

.chain-visualization {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.chain-level {
  display: flex;
  align-items: stretch;
  min-height: 70px;
}

.level-line {
  width: 40px;
  position: relative;
}

.level-line::before {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  width: 2px;
  height: 100%;
  background: #dcdfe6;
}

.chain-level:first-child .level-line::before {
  top: 50%;
  height: 50%;
}

.chain-level:last-child .level-line::before {
  height: 50%;
}

.level-content {
  flex: 1;
  padding: 12px 16px;
  margin: 8px 0;
  border-radius: 12px;
  background: #f8f9fa;
  border-left: 4px solid;
  transition: all 0.2s ease;
}

.level-content.healthy { border-left-color: #67C23A; }
.level-content.warning { border-left-color: #E6A23C; }
.level-content.critical { border-left-color: #F56C6C; }

.level-name {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 4px;
}

.level-status {
  font-size: 11px;
  font-weight: 500;
  margin-bottom: 4px;
}

.level-components {
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

.pagination-wrapper {
  padding: 16px 20px;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #ebeef5;
}

/* Detail Dialog */
.component-detail {
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

/* Topology Diagram */
.topology-diagram {
  padding: 20px;
}

.topology-level {
  text-align: center;
  margin-bottom: 20px;
}

.topology-level-name {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 12px;
  color: #606266;
}

.topology-components {
  display: flex;
  justify-content: center;
  gap: 20px;
  flex-wrap: wrap;
}

.topology-component {
  padding: 12px 20px;
  border-radius: 12px;
  background: #f8f9fa;
  text-align: center;
  min-width: 140px;
}

.topology-component.healthy { border: 2px solid #67C23A; }
.topology-component.warning { border: 2px solid #E6A23C; }
.topology-component.critical { border: 2px solid #F56C6C; }

.comp-name {
  font-weight: 500;
  font-size: 13px;
  margin-bottom: 4px;
}

.comp-status {
  font-size: 11px;
  font-weight: 600;
}

.topology-arrow {
  font-size: 20px;
  color: #c0c4cc;
  margin: 8px 0;
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
  .power-chain-faults {
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

  .chain-visualization {
    overflow-x: auto;
  }

  .chain-level {
    min-width: 300px;
  }
}
</style>