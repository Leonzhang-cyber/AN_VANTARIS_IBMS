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
        <div class="loading-tip">Valve Control System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="valves-container">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Valves</h2>
        <p class="header-subtitle">Valve Control & Monitoring | Automated Actuators</p>
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
            <div class="overview-label">Total Valves</div>
            <div class="overview-value">{{ stats.total }}</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="overview-card">
          <div class="overview-icon open">
            <el-icon :size="28"><CircleCheck /></el-icon>
          </div>
          <div class="overview-info">
            <div class="overview-label">Open</div>
            <div class="overview-value">{{ stats.open }}</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="overview-card">
          <div class="overview-icon closed">
            <el-icon :size="28"><CircleClose /></el-icon>
          </div>
          <div class="overview-info">
            <div class="overview-label">Closed</div>
            <div class="overview-value">{{ stats.closed }}</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="overview-card">
          <div class="overview-icon fault">
            <el-icon :size="28"><WarningFilled /></el-icon>
          </div>
          <div class="overview-info">
            <div class="overview-label">Fault</div>
            <div class="overview-value">{{ stats.fault }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Valve Control Section -->
    <div class="section-title">
      <span>Valve Control Panel</span>
      <el-radio-group v-model="valveFilter" size="small">
        <el-radio-button label="all">All</el-radio-button>
        <el-radio-button label="open">Open</el-radio-button>
        <el-radio-button label="closed">Closed</el-radio-button>
        <el-radio-button label="fault">Fault</el-radio-button>
      </el-radio-group>
    </div>

    <el-row :gutter="20" class="valves-row">
      <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="valve in filteredValves" :key="valve.id">
        <div class="valve-card" :class="valve.status">
          <div class="valve-header">
            <span class="valve-name">{{ valve.name }}</span>
            <el-tag :type="getStatusTag(valve.status)" size="small">
              {{ getStatusText(valve.status) }}
            </el-tag>
          </div>
          <div class="valve-icon">
            <el-icon :size="48" v-if="valve.status === 'open'"><Switch /></el-icon>
            <el-icon :size="48" v-else-if="valve.status === 'closed'"><Switch /></el-icon>
            <el-icon :size="48" v-else><WarningFilled /></el-icon>
          </div>
          <div class="valve-position">
            <div class="position-label">Valve Position</div>
            <div class="position-value">{{ valve.position }}%</div>
            <el-slider
                v-model="valve.position"
                :min="0"
                :max="100"
                :disabled="valve.status === 'fault'"
                @change="(val) => updateValvePosition(valve, val)"
            />
          </div>
          <div class="valve-parameters">
            <div class="param">
              <span class="label">Type:</span>
              <span class="value">{{ valve.valveType }}</span>
            </div>
            <div class="param">
              <span class="label">Size:</span>
              <span class="value">{{ valve.size }} mm</span>
            </div>
            <div class="param">
              <span class="label">Pressure:</span>
              <span class="value">{{ valve.pressure }} bar</span>
            </div>
            <div class="param">
              <span class="label">Flow Rate:</span>
              <span class="value">{{ valve.flowRate }} m³/h</span>
            </div>
            <div class="param">
              <span class="label">Actuator:</span>
              <span class="value">{{ valve.actuatorType }}</span>
            </div>
          </div>
          <div class="valve-actions">
            <el-button
                type="success"
                size="small"
                @click="controlValve(valve, 'open')"
                :disabled="valve.status === 'open' || valve.status === 'fault'"
            >
              <el-icon><Switch /></el-icon>
              Open
            </el-button>
            <el-button
                type="danger"
                size="small"
                @click="controlValve(valve, 'close')"
                :disabled="valve.status === 'closed' || valve.status === 'fault'"
            >
              <el-icon><Switch /></el-icon>
              Close
            </el-button>
            <el-button
                v-if="valve.status === 'fault'"
                type="warning"
                size="small"
                @click="resetValve(valve)"
            >
              <el-icon><RefreshRight /></el-icon>
              Reset
            </el-button>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Performance Charts -->
    <el-row :gutter="20" class="charts-row">
      <el-col :xs="24" :md="14">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Valve Position & Flow Trend (Last 24 Hours)</span>
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
              <span>Valve Status Distribution</span>
            </div>
          </template>
          <div ref="statusChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Valve Details Table -->
    <el-card shadow="hover" class="table-card">
      <template #header>
        <div class="card-header">
          <span>Valve Details</span>
          <div class="table-controls">
            <el-input v-model="searchText" placeholder="Search valve..." style="width: 200px" clearable>
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-select v-model="typeFilter" placeholder="Filter by type" style="width: 150px" clearable>
              <el-option label="All Types" value="all" />
              <el-option label="Ball Valve" value="Ball Valve" />
              <el-option label="Gate Valve" value="Gate Valve" />
              <el-option label="Globe Valve" value="Globe Valve" />
              <el-option label="Butterfly Valve" value="Butterfly Valve" />
              <el-option label="Check Valve" value="Check Valve" />
            </el-select>
          </div>
        </div>
      </template>
      <el-table :data="paginatedValves" stripe border style="width: 100%">
        <el-table-column prop="name" label="Valve Name" min-width="150" />
        <el-table-column prop="valveType" label="Type" min-width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.valveType)" size="small">{{ row.valveType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="size" label="Size (mm)" min-width="100" sortable />
        <el-table-column prop="position" label="Position" min-width="120" sortable>
          <template #default="{ row }">
            <el-progress :percentage="row.position" :color="getPositionColor(row.position)" :stroke-width="8" />
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" min-width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="pressure" label="Pressure (bar)" min-width="100" sortable />
        <el-table-column prop="flowRate" label="Flow (m³/h)" min-width="100" sortable />
        <el-table-column prop="actuatorType" label="Actuator" min-width="120" />
        <el-table-column prop="lastActuated" label="Last Actuated" min-width="160" />
        <el-table-column label="Actions" fixed="right" min-width="150">
          <template #default="{ row }">
            <el-button type="success" link size="small" @click="controlValve(row, 'open')" :disabled="row.status === 'open'">
              Open
            </el-button>
            <el-button type="danger" link size="small" @click="controlValve(row, 'close')" :disabled="row.status === 'closed'">
              Close
            </el-button>
            <el-button type="primary" link size="small" @click="viewValveDetails(row)">
              Details
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-container">
        <el-pagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredTableValves.length"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Valve Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`Valve Details - ${selectedValve?.name}`" width="600px">
      <el-descriptions :column="2" border v-if="selectedValve">
        <el-descriptions-item label="Valve Name">{{ selectedValve.name }}</el-descriptions-item>
        <el-descriptions-item label="Valve Type">{{ selectedValve.valveType }}</el-descriptions-item>
        <el-descriptions-item label="Size">{{ selectedValve.size }} mm</el-descriptions-item>
        <el-descriptions-item label="Material">{{ selectedValve.material }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusTag(selectedValve.status)">{{ getStatusText(selectedValve.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Position">{{ selectedValve.position }}%</el-descriptions-item>
        <el-descriptions-item label="Pressure">{{ selectedValve.pressure }} bar</el-descriptions-item>
        <el-descriptions-item label="Flow Rate">{{ selectedValve.flowRate }} m³/h</el-descriptions-item>
        <el-descriptions-item label="Actuator Type">{{ selectedValve.actuatorType }}</el-descriptions-item>
        <el-descriptions-item label="Actuator Torque">{{ selectedValve.actuatorTorque }} Nm</el-descriptions-item>
        <el-descriptions-item label="Last Actuated">{{ selectedValve.lastActuated }}</el-descriptions-item>
        <el-descriptions-item label="Cycle Count">{{ selectedValve.cycleCount }}</el-descriptions-item>
        <el-descriptions-item label="Last Maintenance">{{ selectedValve.lastMaintenance }}</el-descriptions-item>
        <el-descriptions-item label="Next Maintenance">{{ selectedValve.nextMaintenance }}</el-descriptions-item>
      </el-descriptions>
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
  CircleCheck,
  CircleClose,
  WarningFilled,
  Switch,
  RefreshRight,
  Search
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Initializing valve actuators...',
  'Reading position sensors...',
  'Almost ready...'
]

// ==================== Data State ====================
const chartPeriod = ref('hour')
const valveFilter = ref('all')
const searchText = ref('')
const typeFilter = ref('all')

interface Valve {
  id: number
  name: string
  valveType: string
  size: number
  material: string
  status: 'open' | 'closed' | 'fault'
  position: number
  pressure: number
  flowRate: number
  actuatorType: string
  actuatorTorque: number
  lastActuated: string
  cycleCount: number
  lastMaintenance: string
  nextMaintenance: string
}

const valves = ref<Valve[]>([])

const stats = computed(() => ({
  total: valves.value.length,
  open: valves.value.filter(v => v.status === 'open').length,
  closed: valves.value.filter(v => v.status === 'closed').length,
  fault: valves.value.filter(v => v.status === 'fault').length
}))

const filteredValves = computed(() => {
  if (valveFilter.value === 'all') return valves.value
  return valves.value.filter(v => v.status === valveFilter.value)
})

const filteredTableValves = computed(() => {
  let filtered = valves.value
  if (searchText.value) {
    filtered = filtered.filter(v =>
        v.name.toLowerCase().includes(searchText.value.toLowerCase()) ||
        v.valveType.toLowerCase().includes(searchText.value.toLowerCase())
    )
  }
  if (typeFilter.value !== 'all') {
    filtered = filtered.filter(v => v.valveType === typeFilter.value)
  }
  return filtered
})

const pagination = ref({ currentPage: 1, pageSize: 10 })
const paginatedValves = computed(() => {
  const start = (pagination.value.currentPage - 1) * pagination.value.pageSize
  return filteredTableValves.value.slice(start, start + pagination.value.pageSize)
})

// Generate mock valves
const generateValves = (): Valve[] => {
  const valveNames = [
    'Main Inlet Valve', 'Outlet Control Valve', 'Bypass Valve',
    'Drain Valve', 'Pressure Relief Valve', 'Isolation Valve A',
    'Isolation Valve B', 'Flow Control Valve', 'Return Valve',
    'Makeup Water Valve', 'Emergency Shutoff', 'Zone Valve 1',
    'Zone Valve 2', 'Zone Valve 3', 'Cooling Water Valve'
  ]

  const valveTypes = ['Ball Valve', 'Gate Valve', 'Globe Valve', 'Butterfly Valve', 'Check Valve']
  const actuatorTypes = ['Electric', 'Pneumatic', 'Hydraulic', 'Manual']
  const materials = ['Stainless Steel', 'Cast Iron', 'Brass', 'Bronze', 'Carbon Steel']
  const statuses: ('open' | 'closed' | 'fault')[] = ['open', 'closed', 'open', 'closed', 'open', 'closed', 'fault', 'open', 'closed', 'open', 'closed', 'open', 'closed', 'open', 'closed']

  return valveNames.map((name, idx) => {
    const position = statuses[idx % statuses.length] === 'open' ? 80 + Math.random() * 20 : Math.random() * 20
    const pressure = parseFloat((2 + Math.random() * 8).toFixed(1))
    const flowRate = parseFloat((10 + Math.random() * 90).toFixed(1))

    return {
      id: idx + 1,
      name: name,
      valveType: valveTypes[idx % valveTypes.length],
      size: [50, 80, 100, 150, 200][idx % 5],
      material: materials[idx % materials.length],
      status: statuses[idx % statuses.length],
      position: parseFloat(position.toFixed(1)),
      pressure: pressure,
      flowRate: flowRate,
      actuatorType: actuatorTypes[idx % actuatorTypes.length],
      actuatorTorque: [100, 250, 500, 1000][idx % 4],
      lastActuated: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toLocaleString(),
      cycleCount: Math.floor(100 + Math.random() * 1000),
      lastMaintenance: '2024-01-15',
      nextMaintenance: '2024-04-15'
    }
  })
}

// Helper functions
const getStatusTag = (status: string) => {
  const map: Record<string, string> = { open: 'success', closed: 'info', fault: 'danger' }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = { open: 'Open', closed: 'Closed', fault: 'Fault' }
  return map[status] || status
}

const getTypeTag = (type: string) => {
  const map: Record<string, string> = {
    'Ball Valve': 'primary',
    'Gate Valve': 'success',
    'Globe Valve': 'warning',
    'Butterfly Valve': 'danger',
    'Check Valve': 'info'
  }
  return map[type] || 'info'
}

const getPositionColor = (position: number) => {
  if (position > 80) return '#67C23A'
  if (position > 20) return '#E6A23C'
  return '#F56C6C'
}

// Valve control actions
const controlValve = (valve: Valve, action: 'open' | 'close') => {
  const newPosition = action === 'open' ? 100 : 0
  const newStatus = action === 'open' ? 'open' : 'closed'

  ElMessageBox.confirm(
      `${action === 'open' ? 'Open' : 'Close'} valve "${valve.name}"?`,
      'Confirm Control',
      { confirmButtonText: 'Confirm', cancelButtonText: 'Cancel', type: 'info' }
  ).then(() => {
    valve.position = newPosition
    valve.status = newStatus
    valve.lastActuated = new Date().toLocaleString()
    valve.cycleCount++
    ElMessage.success(`Valve "${valve.name}" ${action}ed successfully`)
    updateStatusChart()
  }).catch(() => {})
}

const updateValvePosition = (valve: Valve, position: number) => {
  if (position === 0) {
    valve.status = 'closed'
  } else if (position === 100) {
    valve.status = 'open'
  } else {
    valve.status = valve.status === 'fault' ? 'closed' : valve.status
  }
  valve.lastActuated = new Date().toLocaleString()
  ElMessage.info(`Valve "${valve.name}" position set to ${position}%`)
  updateStatusChart()
}

const resetValve = (valve: Valve) => {
  ElMessageBox.confirm(`Reset valve "${valve.name}"?`, 'Confirm', {
    confirmButtonText: 'Reset',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    valve.status = 'closed'
    valve.position = 0
    ElMessage.success(`Valve "${valve.name}" reset successfully`)
    updateStatusChart()
  }).catch(() => {})
}

const viewValveDetails = (valve: Valve) => {
  selectedValve.value = valve
  detailDialogVisible.value = true
}

// ==================== Chart Functions ====================
const trendChartRef = ref<HTMLElement>()
const statusChartRef = ref<HTMLElement>()

let trendChart: echarts.ECharts | null = null
let statusChart: echarts.ECharts | null = null

const initCharts = () => {
  nextTick(() => {
    if (trendChartRef.value) {
      if (trendChart) trendChart.dispose()
      trendChart = echarts.init(trendChartRef.value)
      updateTrendChart()
    }

    if (statusChartRef.value) {
      if (statusChart) statusChart.dispose()
      statusChart = echarts.init(statusChartRef.value)
      updateStatusChart()
    }
  })
}

const updateTrendChart = () => {
  let positionData: number[] = []
  let flowData: number[] = []
  let xAxisData: string[] = []

  if (chartPeriod.value === 'hour') {
    xAxisData = Array.from({ length: 24 }, (_, i) => `${i}:00`)
    positionData = Array.from({ length: 24 }, () => parseFloat((40 + Math.random() * 50).toFixed(1)))
    flowData = Array.from({ length: 24 }, () => parseFloat((30 + Math.random() * 60).toFixed(1)))
  } else if (chartPeriod.value === 'day') {
    xAxisData = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    positionData = [65, 70, 55, 80, 85, 60, 45]
    flowData = [55, 60, 45, 70, 75, 50, 35]
  } else {
    xAxisData = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
    positionData = [65, 70, 55, 80]
    flowData = [55, 60, 45, 70]
  }

  trendChart?.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Valve Position (%)', 'Flow Rate (m³/h)'] },
    xAxis: { type: 'category', data: xAxisData },
    yAxis: [
      { type: 'value', name: 'Position (%)', min: 0, max: 100 },
      { type: 'value', name: 'Flow Rate (m³/h)' }
    ],
    series: [
      {
        name: 'Valve Position (%)',
        type: 'line',
        data: positionData,
        smooth: true,
        lineStyle: { color: '#409EFF', width: 3 },
        areaStyle: { opacity: 0.1 },
        yAxisIndex: 0
      },
      {
        name: 'Flow Rate (m³/h)',
        type: 'line',
        data: flowData,
        smooth: true,
        lineStyle: { color: '#67C23A', width: 3 },
        yAxisIndex: 1
      }
    ]
  })
}

const updateStatusChart = () => {
  statusChart?.setOption({
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: '55%',
      data: [
        { value: stats.value.open, name: 'Open', itemStyle: { color: '#67C23A' } },
        { value: stats.value.closed, name: 'Closed', itemStyle: { color: '#909399' } },
        { value: stats.value.fault, name: 'Fault', itemStyle: { color: '#F56C6C' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  })
}

// ==================== Actions ====================
const detailDialogVisible = ref(false)
const selectedValve = ref<Valve | null>(null)

const refreshData = () => {
  valves.value = generateValves()
  updateStatusChart()
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
      valves.value = generateValves()
      initCharts()
    }, 400)
  }, 2000)
})

watch([trendChartRef, statusChartRef], () => {
  window.addEventListener('resize', () => {
    trendChart?.resize()
    statusChart?.resize()
  })
})

watch([valveFilter, searchText, typeFilter], () => {
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
.valves-container {
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
.overview-icon.open { background: rgba(103, 194, 58, 0.1); color: #67C23A; }
.overview-icon.closed { background: rgba(144, 147, 153, 0.1); color: #909399; }
.overview-icon.fault { background: rgba(245, 108, 108, 0.1); color: #F56C6C; }

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

/* Valve Cards */
.valves-row {
  margin-bottom: 20px;
}

.valve-card {
  background: white;
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: all 0.3s ease;
  border-left: 4px solid #67C23A;
}

.valve-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 28px rgba(0,0,0,0.12);
}

.valve-card.open { border-left-color: #67C23A; }
.valve-card.closed { border-left-color: #909399; }
.valve-card.fault { border-left-color: #F56C6C; background: rgba(245, 108, 108, 0.02); }

.valve-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.valve-name {
  font-weight: 600;
  font-size: 16px;
  color: #1f2f3d;
}

.valve-icon {
  text-align: center;
  margin: 8px 0;
  color: #409EFF;
}

.valve-card.closed .valve-icon { color: #909399; }
.valve-card.fault .valve-icon { color: #F56C6C; }

.valve-position {
  margin-bottom: 16px;
}

.position-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
  text-align: center;
}

.position-value {
  text-align: center;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
}

.valve-parameters {
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

.valve-actions {
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
  flex-wrap: wrap;
  gap: 12px;
}

.table-controls {
  display: flex;
  gap: 12px;
}

.table-card {
  border-radius: 16px;
}

.pagination-container {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>