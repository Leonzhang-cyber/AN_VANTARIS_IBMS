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
        <div class="loading-tip">Distribution Board Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="distribution-board-container">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Distribution Board</h2>
        <p class="header-subtitle">DB-01 | Main Distribution Panel | 400V / 50Hz</p>
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

    <!-- Board Info Row -->
    <el-row :gutter="20" class="board-info-row">
      <el-col :xs="24" :sm="12" :md="8">
        <div class="board-info-card">
          <div class="board-info-icon">
            <el-icon :size="28"><Grid /></el-icon>
          </div>
          <div class="board-info-content">
            <div class="board-info-label">Board Type</div>
            <div class="board-info-value">TTA - Low Voltage</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8">
        <div class="board-info-card">
          <div class="board-info-icon">
            <el-icon :size="28"><Location /></el-icon>
          </div>
          <div class="board-info-content">
            <div class="board-info-label">Location</div>
            <div class="board-info-value">Building A, Floor 2</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8">
        <div class="board-info-card">
          <div class="board-info-icon">
            <el-icon :size="28"><Calendar /></el-icon>
          </div>
          <div class="board-info-content">
            <div class="board-info-label">Last Maintenance</div>
            <div class="board-info-value">{{ lastMaintenance }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Main Metrics Row -->
    <el-row :gutter="20" class="metrics-row">
      <el-col :xs="24" :sm="12" :md="6">
        <div class="metric-card total-load">
          <div class="metric-icon">
            <el-icon :size="28"><Lightning /></el-icon>
          </div>
          <div class="metric-info">
            <div class="metric-label">Total Load</div>
            <div class="metric-value">{{ formatNumber(stats.totalLoad) }} <span class="metric-unit">kW</span></div>
            <div class="metric-trend">{{ stats.loadPercent }}% of Capacity</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="metric-card total-current">
          <div class="metric-icon">
            <el-icon :size="28"><Connection /></el-icon>
          </div>
          <div class="metric-info">
            <div class="metric-label">Total Current</div>
            <div class="metric-value">{{ formatNumber(stats.totalCurrent) }} <span class="metric-unit">A</span></div>
            <div class="metric-trend">Max: {{ stats.maxCurrent }} A</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="metric-card voltage">
          <div class="metric-icon">
            <el-icon :size="28"><Histogram /></el-icon>
          </div>
          <div class="metric-info">
            <div class="metric-label">Voltage</div>
            <div class="metric-value">{{ stats.avgVoltage }} <span class="metric-unit">V</span></div>
            <div class="metric-trend">Balanced: {{ stats.voltageBalance }}%</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="metric-card temperature">
          <div class="metric-icon">
            <el-icon :size="28"><InfoFilled /></el-icon>
          </div>
          <div class="metric-info">
            <div class="metric-label">Temperature</div>
            <div class="metric-value">{{ stats.temperature }} <span class="metric-unit">°C</span></div>
            <div class="metric-trend" :class="stats.temperature > 45 ? 'warning' : 'normal'">
              {{ stats.temperature > 45 ? 'High' : 'Normal' }}
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Phase Details Row -->
    <el-row :gutter="20" class="phase-row">
      <el-col :xs="24" :sm="8" v-for="phase in phases" :key="phase.name">
        <div class="phase-card" :class="phase.status">
          <div class="phase-header">
            <span class="phase-name">Phase {{ phase.name }}</span>
            <el-tag :type="phase.status === 'normal' ? 'success' : 'danger'" size="small">
              {{ phase.status === 'normal' ? 'Normal' : 'Alert' }}
            </el-tag>
          </div>
          <div class="phase-details">
            <div class="phase-detail">
              <span class="label">Voltage:</span>
              <span class="value">{{ phase.voltage }} V</span>
            </div>
            <div class="phase-detail">
              <span class="label">Current:</span>
              <span class="value">{{ phase.current }} A</span>
            </div>
            <div class="phase-detail">
              <span class="label">Load:</span>
              <span class="value">{{ phase.load }} kW</span>
            </div>
            <div class="phase-detail">
              <span class="label">PF:</span>
              <span class="value">{{ phase.powerFactor }}</span>
            </div>
          </div>
          <div class="phase-progress">
            <el-progress
                :percentage="phase.loadPercent"
                :color="phase.loadPercent > 80 ? '#F56C6C' : (phase.loadPercent > 60 ? '#E6A23C' : '#67C23A')"
                :stroke-width="8"
            />
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Charts Row -->
    <el-row :gutter="20" class="charts-row">
      <el-col :xs="24" :md="16">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Current & Power Trend (Last 24 Hours)</span>
              <el-radio-group v-model="chartPeriod" size="small" @change="updateChartPeriod">
                <el-radio-button label="hour">Hourly</el-radio-button>
                <el-radio-button label="day">Daily</el-radio-button>
                <el-radio-button label="week">Weekly</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="8">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Load Distribution by Circuit</span>
            </div>
          </template>
          <div ref="loadChartRef" class="chart-container-small"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Circuit Breakers Section -->
    <el-card shadow="hover" class="circuits-card">
      <template #header>
        <div class="card-header">
          <span>Circuit Breakers</span>
          <div class="circuits-stats">
            <el-tag type="success" size="small">ON: {{ circuits.filter(c => c.status === 'on').length }}</el-tag>
            <el-tag type="info" size="small">OFF: {{ circuits.filter(c => c.status === 'off').length }}</el-tag>
            <el-tag type="danger" size="small">Tripped: {{ circuits.filter(c => c.status === 'tripped').length }}</el-tag>
          </div>
        </div>
      </template>

      <el-row :gutter="12">
        <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="circuit in paginatedCircuits" :key="circuit.id">
          <div class="circuit-card" :class="circuit.status">
            <div class="circuit-header">
              <span class="circuit-number">CB-{{ String(circuit.id).padStart(2, '0') }}</span>
              <el-tag :type="getCircuitStatusType(circuit.status)" size="small">
                {{ getCircuitStatusText(circuit.status) }}
              </el-tag>
            </div>
            <div class="circuit-name">{{ circuit.name }}</div>
            <div class="circuit-details">
              <div class="circuit-detail">
                <span class="label">Load:</span>
                <span class="value">{{ circuit.load }} kW</span>
              </div>
              <div class="circuit-detail">
                <span class="label">Current:</span>
                <span class="value">{{ circuit.current }} A</span>
              </div>
              <div class="circuit-detail">
                <span class="label">Rating:</span>
                <span class="value">{{ circuit.rating }} A</span>
              </div>
            </div>
            <div class="circuit-progress">
              <el-progress
                  :percentage="circuit.loadPercent"
                  :color="getCircuitProgressColor(circuit.loadPercent)"
                  :stroke-width="6"
                  :show-text="false"
              />
              <span class="progress-text">{{ circuit.loadPercent }}%</span>
            </div>
            <div class="circuit-actions">
              <el-switch
                  v-model="circuit.status"
                  active-value="on"
                  inactive-value="off"
                  active-text="ON"
                  inactive-text="OFF"
                  @change="toggleCircuit(circuit)"
                  :disabled="circuit.status === 'tripped'"
              />
              <el-button type="primary" link size="small" @click="viewCircuitDetails(circuit)">
                Details
              </el-button>
              <el-button
                  v-if="circuit.status === 'tripped'"
                  type="warning"
                  link
                  size="small"
                  @click="resetCircuit(circuit)"
              >
                Reset
              </el-button>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- Pagination -->
      <div class="pagination-container">
        <el-pagination
            v-model:current-page="circuitsPagination.currentPage"
            v-model:page-size="circuitsPagination.pageSize"
            :page-sizes="[8, 16, 24, 32]"
            :total="filteredCircuits.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleCircuitsSizeChange"
            @current-change="handleCircuitsCurrentChange"
        />
      </div>
    </el-card>

    <!-- Energy & Power Quality -->
    <el-row :gutter="20">
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" class="energy-card">
          <template #header>
            <div class="card-header">
              <span>Energy Consumption</span>
            </div>
          </template>
          <div class="energy-stats">
            <div class="energy-item">
              <div class="energy-label">Today</div>
              <div class="energy-value">{{ stats.energyToday }} <span class="unit">kWh</span></div>
            </div>
            <div class="energy-item">
              <div class="energy-label">This Week</div>
              <div class="energy-value">{{ stats.energyWeek }} <span class="unit">kWh</span></div>
            </div>
            <div class="energy-item">
              <div class="energy-label">This Month</div>
              <div class="energy-value">{{ stats.energyMonth }} <span class="unit">kWh</span></div>
            </div>
            <div class="energy-item">
              <div class="energy-label">This Year</div>
              <div class="energy-value">{{ stats.energyYear }} <span class="unit">kWh</span></div>
            </div>
          </div>
          <div class="energy-footer">
            <span>CO₂ Saved: {{ stats.co2Saved }} kg</span>
            <span>Cost: ${{ stats.energyCost }}</span>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" class="quality-card">
          <template #header>
            <div class="card-header">
              <span>Power Quality Metrics</span>
              <el-button text @click="refreshQuality">Refresh</el-button>
            </div>
          </template>
          <el-table :data="qualityMetrics" stripe border size="small">
            <el-table-column prop="metric" label="Metric" width="140" />
            <el-table-column prop="value" label="Value" />
            <el-table-column prop="status" label="Status">
              <template #default="{ row }">
                <el-tag :type="row.status === 'Normal' ? 'success' : 'danger'" size="small">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- Circuit Detail Dialog -->
    <el-dialog v-model="circuitDialogVisible" :title="`Circuit Details - ${selectedCircuit?.name}`" width="550px">
      <el-descriptions :column="2" border v-if="selectedCircuit">
        <el-descriptions-item label="Circuit Number">CB-{{ String(selectedCircuit.id).padStart(2, '0') }}</el-descriptions-item>
        <el-descriptions-item label="Circuit Name">{{ selectedCircuit.name }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getCircuitStatusType(selectedCircuit.status)">{{ getCircuitStatusText(selectedCircuit.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Load">{{ selectedCircuit.load }} kW</el-descriptions-item>
        <el-descriptions-item label="Current">{{ selectedCircuit.current }} A</el-descriptions-item>
        <el-descriptions-item label="Rated Current">{{ selectedCircuit.rating }} A</el-descriptions-item>
        <el-descriptions-item label="Load Percentage">{{ selectedCircuit.loadPercent }}%</el-descriptions-item>
        <el-descriptions-item label="Voltage">{{ selectedCircuit.voltage || 230 }} V</el-descriptions-item>
        <el-descriptions-item label="Power Factor">{{ selectedCircuit.powerFactor || 0.92 }}</el-descriptions-item>
        <el-descriptions-item label="Energy Today">{{ selectedCircuit.energyToday || 0 }} kWh</el-descriptions-item>
        <el-descriptions-item label="Energy Month">{{ selectedCircuit.energyMonth || 0 }} kWh</el-descriptions-item>
        <el-descriptions-item label="Last Trip" :span="2">{{ selectedCircuit.lastTrip || 'Never' }}</el-descriptions-item>
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
  Location,
  Calendar,
  Lightning,
  Connection,
  Histogram,
  InfoFilled
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Initializing distribution board...',
  'Loading circuit data...',
  'Almost ready...'
]

// ==================== Data State ====================
const chartPeriod = ref('hour')
const lastMaintenance = ref('2024-01-10')

interface Circuit {
  id: number
  name: string
  status: 'on' | 'off' | 'tripped'
  load: number
  current: number
  rating: number
  loadPercent: number
  voltage?: number
  powerFactor?: number
  energyToday?: number
  energyMonth?: number
  lastTrip?: string
}

interface Phase {
  name: string
  voltage: number
  current: number
  load: number
  powerFactor: number
  loadPercent: number
  status: 'normal' | 'alert'
}

const stats = ref({
  totalLoad: 0,
  totalCurrent: 0,
  maxCurrent: 0,
  avgVoltage: 0,
  voltageBalance: 0,
  temperature: 0,
  loadPercent: 0,
  energyToday: 0,
  energyWeek: 0,
  energyMonth: 0,
  energyYear: 0,
  co2Saved: 0,
  energyCost: 0
})

const phases = ref<Phase[]>([])
const circuits = ref<Circuit[]>([])
const qualityMetrics = ref([
  { metric: 'Frequency', value: '50.0 Hz', status: 'Normal' },
  { metric: 'THD Voltage', value: '2.3%', status: 'Normal' },
  { metric: 'THD Current', value: '3.8%', status: 'Normal' },
  { metric: 'Power Factor', value: '0.92', status: 'Normal' },
  { metric: 'Voltage Imbalance', value: '1.2%', status: 'Normal' }
])

// Filters & Pagination
const circuitSearch = ref('')
const circuitFilter = ref('all')

const circuitsPagination = ref({
  currentPage: 1,
  pageSize: 8
})

const filteredCircuits = computed(() => {
  let filtered = circuits.value
  if (circuitSearch.value) {
    filtered = filtered.filter(c => c.name.toLowerCase().includes(circuitSearch.value.toLowerCase()))
  }
  if (circuitFilter.value !== 'all') {
    filtered = filtered.filter(c => c.status === circuitFilter.value)
  }
  return filtered
})

const paginatedCircuits = computed(() => {
  const start = (circuitsPagination.value.currentPage - 1) * circuitsPagination.value.pageSize
  return filteredCircuits.value.slice(start, start + circuitsPagination.value.pageSize)
})

// Generate mock circuits
const generateCircuits = (): Circuit[] => {
  const circuitNames = [
    'Lighting Floor 1', 'Lighting Floor 2', 'Lighting Floor 3', 'Office Outlets',
    'Meeting Room', 'Conference Hall', 'IT Room', 'Server Room',
    'HVAC Unit 1', 'HVAC Unit 2', 'Elevator', 'Escalator',
    'Fire Alarm', 'Emergency Lights', 'Kitchen Equipment', 'Security System',
    'Data Center', 'Network Switches', 'Pump Room', 'Workshop'
  ]

  return circuitNames.map((name, idx) => {
    const rating = [16, 16, 16, 20, 10, 25, 32, 63, 40, 40, 32, 32, 10, 10, 25, 16, 100, 20, 25, 50][idx % 20]
    const current = parseFloat((Math.random() * rating * 0.7 + rating * 0.1).toFixed(1))
    const loadPercent = parseFloat(((current / rating) * 100).toFixed(1))
    const statuses: ('on' | 'off' | 'tripped')[] = ['on', 'on', 'on', 'on', 'on', 'on', 'off', 'on', 'on', 'on', 'on', 'tripped', 'on', 'on', 'on', 'off', 'on', 'on', 'on', 'on']

    return {
      id: idx + 1,
      name: name,
      status: statuses[idx % statuses.length],
      load: parseFloat((current * 0.23).toFixed(1)),
      current: current,
      rating: rating,
      loadPercent: loadPercent,
      voltage: 230,
      powerFactor: parseFloat((0.85 + Math.random() * 0.1).toFixed(2)),
      energyToday: parseFloat((Math.random() * 100).toFixed(1)),
      energyMonth: parseFloat((Math.random() * 3000).toFixed(1)),
      lastTrip: idx === 11 ? '2024-01-14 09:45:22' : undefined
    }
  })
}

// Generate phases data
const generatePhases = (totalLoad: number, totalCurrent: number): Phase[] => {
  const phasesData: Phase[] = []
  const loads = [totalLoad * 0.34, totalLoad * 0.33, totalLoad * 0.33]
  const currents = [totalCurrent * 0.34, totalCurrent * 0.33, totalCurrent * 0.33]

  ;['R', 'Y', 'B'].forEach((name, idx) => {
    const loadPercent = parseFloat(((loads[idx] / 150) * 100).toFixed(1))
    phasesData.push({
      name: name,
      voltage: 400 + (Math.random() - 0.5) * 8,
      current: parseFloat(currents[idx].toFixed(1)),
      load: parseFloat(loads[idx].toFixed(1)),
      powerFactor: parseFloat((0.85 + Math.random() * 0.1).toFixed(2)),
      loadPercent: loadPercent,
      status: loadPercent > 85 ? 'alert' : 'normal'
    })
  })
  return phasesData
}

// Update all stats
const updateStats = () => {
  const totalLoad = circuits.value.reduce((sum, c) => sum + (c.status === 'on' ? c.load : 0), 0)
  const totalCurrent = circuits.value.reduce((sum, c) => sum + (c.status === 'on' ? c.current : 0), 0)
  const maxCurrent = Math.max(...circuits.value.filter(c => c.status === 'on').map(c => c.current), 0)

  stats.value.totalLoad = parseFloat(totalLoad.toFixed(1))
  stats.value.totalCurrent = parseFloat(totalCurrent.toFixed(1))
  stats.value.maxCurrent = parseFloat(maxCurrent.toFixed(1))
  stats.value.loadPercent = parseFloat(((totalLoad / 250) * 100).toFixed(1))

  const voltages = [395, 400, 398]
  stats.value.avgVoltage = Math.round(voltages.reduce((a, b) => a + b, 0) / 3)
  const maxVoltage = Math.max(...voltages)
  const minVoltage = Math.min(...voltages)
  stats.value.voltageBalance = parseFloat((100 - ((maxVoltage - minVoltage) / maxVoltage * 100)).toFixed(1))

  stats.value.temperature = parseFloat((38 + Math.random() * 8).toFixed(1))

  stats.value.energyToday = parseFloat((Math.random() * 800 + 400).toFixed(1))
  stats.value.energyWeek = parseFloat((Math.random() * 5000 + 3000).toFixed(1))
  stats.value.energyMonth = parseFloat((Math.random() * 20000 + 10000).toFixed(1))
  stats.value.energyYear = parseFloat((Math.random() * 200000 + 100000).toFixed(1))
  stats.value.co2Saved = Math.round(stats.value.energyYear * 0.4)
  stats.value.energyCost = parseFloat((stats.value.energyMonth * 0.12).toFixed(0))

  phases.value = generatePhases(stats.value.totalLoad, stats.value.totalCurrent)
}

// ==================== Chart Functions ====================
const trendChartRef = ref<HTMLElement>()
const loadChartRef = ref<HTMLElement>()
let trendChart: echarts.ECharts | null = null
let loadChart: echarts.ECharts | null = null

const initCharts = () => {
  nextTick(() => {
    if (trendChartRef.value) {
      if (trendChart) trendChart.dispose()
      trendChart = echarts.init(trendChartRef.value)
      updateTrendChart()
    }

    if (loadChartRef.value) {
      if (loadChart) loadChart.dispose()
      loadChart = echarts.init(loadChartRef.value)
      updateLoadChart()
    }
  })
}

const updateTrendChart = () => {
  let currentData: number[] = []
  let powerData: number[] = []
  let xAxisData: string[] = []

  if (chartPeriod.value === 'hour') {
    xAxisData = Array.from({ length: 24 }, (_, i) => `${i}:00`)
    currentData = Array.from({ length: 24 }, () => parseFloat((Math.random() * 150 + 80).toFixed(1)))
    powerData = Array.from({ length: 24 }, () => parseFloat((Math.random() * 40 + 20).toFixed(1)))
  } else if (chartPeriod.value === 'day') {
    xAxisData = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    currentData = [125, 138, 132, 145, 158, 140, 118]
    powerData = [32, 35, 34, 38, 42, 36, 30]
  } else {
    xAxisData = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
    currentData = [125, 138, 132, 145]
    powerData = [32, 35, 34, 38]
  }

  trendChart?.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Current (A)', 'Power (kW)'] },
    xAxis: { type: 'category', data: xAxisData },
    yAxis: [{ type: 'value', name: 'Current (A)' }, { type: 'value', name: 'Power (kW)' }],
    series: [
      {
        name: 'Current (A)',
        type: 'line',
        data: currentData,
        smooth: true,
        lineStyle: { color: '#409EFF', width: 3 },
        areaStyle: { opacity: 0.1 },
        symbol: 'circle',
        symbolSize: 6
      },
      {
        name: 'Power (kW)',
        type: 'line',
        data: powerData,
        smooth: true,
        lineStyle: { color: '#67C23A', width: 3 },
        yAxisIndex: 1,
        symbol: 'diamond',
        symbolSize: 6
      }
    ]
  })
}

const updateLoadChart = () => {
  const categoryLoads: Record<string, number> = {}
  circuits.value.forEach(circuit => {
    if (circuit.status === 'on') {
      const category = circuit.name.includes('Lighting') ? 'Lighting' :
          circuit.name.includes('HVAC') ? 'HVAC' :
              circuit.name.includes('IT') || circuit.name.includes('Server') || circuit.name.includes('Data') ? 'IT Equipment' :
                  'Others'
      categoryLoads[category] = (categoryLoads[category] || 0) + circuit.load
    }
  })

  const data = Object.entries(categoryLoads).map(([name, value]) => ({ name, value }))

  loadChart?.setOption({
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: '55%',
      data: data,
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  })
}

const updateChartPeriod = () => {
  updateTrendChart()
}

// ==================== Circuit Functions ====================
const circuitDialogVisible = ref(false)
const selectedCircuit = ref<Circuit | null>(null)

const getCircuitStatusType = (status: string) => {
  const map: Record<string, string> = { on: 'success', off: 'info', tripped: 'danger' }
  return map[status] || 'info'
}

const getCircuitStatusText = (status: string) => {
  const map: Record<string, string> = { on: 'ON', off: 'OFF', tripped: 'TRIPPED' }
  return map[status] || status
}

const getCircuitProgressColor = (percent: number) => {
  if (percent < 60) return '#67C23A'
  if (percent < 85) return '#E6A23C'
  return '#F56C6C'
}

const toggleCircuit = (circuit: Circuit) => {
  const action = circuit.status === 'on' ? 'OFF' : 'ON'
  ElMessage.success(`Circuit "${circuit.name}" turned ${action}`)
  updateStats()
  updateLoadChart()
}

const resetCircuit = (circuit: Circuit) => {
  ElMessageBox.confirm(`Reset circuit "${circuit.name}"?`, 'Confirm', {
    confirmButtonText: 'Reset',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    circuit.status = 'on'
    circuit.load = parseFloat((circuit.rating * 0.23 * (0.4 + Math.random() * 0.3)).toFixed(1))
    circuit.current = parseFloat((circuit.load / 0.23).toFixed(1))
    circuit.loadPercent = parseFloat(((circuit.current / circuit.rating) * 100).toFixed(1))
    circuit.lastTrip = undefined
    updateStats()
    updateLoadChart()
    ElMessage.success('Circuit reset successfully')
  }).catch(() => {})
}

const viewCircuitDetails = (circuit: Circuit) => {
  selectedCircuit.value = circuit
  circuitDialogVisible.value = true
}

// ==================== Actions ====================
const refreshQuality = () => {
  qualityMetrics.value = [
    { metric: 'Frequency', value: `${(49.8 + Math.random() * 0.4).toFixed(1)} Hz`, status: 'Normal' },
    { metric: 'THD Voltage', value: `${(1.5 + Math.random() * 2).toFixed(1)}%`, status: Math.random() > 0.8 ? 'Abnormal' : 'Normal' },
    { metric: 'THD Current', value: `${(2 + Math.random() * 3).toFixed(1)}%`, status: 'Normal' },
    { metric: 'Power Factor', value: `${(0.85 + Math.random() * 0.1).toFixed(2)}`, status: 'Normal' },
    { metric: 'Voltage Imbalance', value: `${(0.5 + Math.random() * 2).toFixed(1)}%`, status: Math.random() > 0.9 ? 'Abnormal' : 'Normal' }
  ]
  ElMessage.success('Quality metrics refreshed')
}

const refreshData = () => {
  circuits.value = generateCircuits()
  updateStats()
  updateLoadChart()
  updateTrendChart()
  ElMessage.success('Data refreshed')
}

const handleExport = () => {
  ElMessage.success('Report export started')
}

const formatNumber = (num: number) => {
  return num.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })
}

const handleCircuitsSizeChange = () => {
  circuitsPagination.value.currentPage = 1
}

const handleCircuitsCurrentChange = () => {}

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
      circuits.value = generateCircuits()
      updateStats()
      initCharts()
    }, 400)
  }, 2000)
})

watch([trendChartRef, loadChartRef], () => {
  window.addEventListener('resize', () => {
    trendChart?.resize()
    loadChart?.resize()
  })
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
.distribution-board-container {
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

/* Board Info Cards */
.board-info-row {
  margin-bottom: 20px;
}

.board-info-card {
  background: white;
  border-radius: 12px;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.board-info-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(64, 158, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #409EFF;
}

.board-info-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.board-info-value {
  font-size: 16px;
  font-weight: 600;
  color: #1f2f3d;
}

/* Metric Cards */
.metrics-row {
  margin-bottom: 20px;
}

.metric-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: all 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}

.metric-card.total-load { border-left: 4px solid #409EFF; }
.metric-card.total-current { border-left: 4px solid #67C23A; }
.metric-card.voltage { border-left: 4px solid #E6A23C; }
.metric-card.temperature { border-left: 4px solid #F56C6C; }

.metric-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(64, 158, 255, 0.1);
  color: #409EFF;
}

.metric-card.total-current .metric-icon {
  background: rgba(103, 194, 58, 0.1);
  color: #67C23A;
}

.metric-card.voltage .metric-icon {
  background: rgba(230, 162, 60, 0.1);
  color: #E6A23C;
}

.metric-card.temperature .metric-icon {
  background: rgba(245, 108, 108, 0.1);
  color: #F56C6C;
}

.metric-info { flex: 1; }
.metric-label { font-size: 13px; color: #909399; margin-bottom: 4px; }
.metric-value { font-size: 28px; font-weight: 700; color: #1f2f3d; }
.metric-unit { font-size: 14px; font-weight: normal; color: #909399; }
.metric-trend { font-size: 12px; margin-top: 6px; color: #909399; }
.metric-trend.warning { color: #F56C6C; }

/* Phase Cards */
.phase-row {
  margin-bottom: 20px;
}

.phase-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.phase-card.alert {
  border-left: 4px solid #F56C6C;
  background: rgba(245, 108, 108, 0.02);
}

.phase-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.phase-name {
  font-size: 18px;
  font-weight: 600;
  color: #1f2f3d;
}

.phase-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 16px;
}

.phase-detail {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
}

.phase-detail .label { color: #909399; }
.phase-detail .value { font-weight: 500; color: #606266; }

.phase-progress {
  margin-top: 8px;
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

.chart-container-small {
  width: 100%;
  height: 300px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Circuits Card */
.circuits-card {
  border-radius: 16px;
  margin-bottom: 20px;
}

.circuits-stats {
  display: flex;
  gap: 8px;
}

.circuit-card {
  background: #fafafa;
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 12px;
  transition: all 0.3s ease;
  border: 1px solid #e4e7ed;
}

.circuit-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
.circuit-card.on { border-left: 3px solid #67C23A; }
.circuit-card.off { border-left: 3px solid #909399; opacity: 0.7; }
.circuit-card.tripped { border-left: 3px solid #F56C6C; background: rgba(245, 108, 108, 0.05); }

.circuit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.circuit-number {
  font-size: 12px;
  color: #909399;
  font-family: monospace;
}

.circuit-name {
  font-weight: 600;
  font-size: 14px;
  color: #1f2f3d;
  margin-bottom: 12px;
}

.circuit-details {
  margin-bottom: 12px;
}

.circuit-detail {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  margin-bottom: 4px;
}

.circuit-detail .label { color: #909399; }
.circuit-detail .value { font-weight: 500; color: #606266; }

.circuit-progress {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.circuit-progress .el-progress {
  flex: 1;
}

.progress-text {
  font-size: 11px;
  color: #909399;
  min-width: 35px;
}

.circuit-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Energy & Quality */
.energy-card, .quality-card {
  border-radius: 16px;
}

.energy-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  padding: 10px;
}

.energy-item {
  text-align: center;
}

.energy-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.energy-value {
  font-size: 24px;
  font-weight: 700;
  color: #409EFF;
}

.energy-value .unit {
  font-size: 12px;
  font-weight: normal;
  color: #909399;
}

.energy-footer {
  display: flex;
  justify-content: space-between;
  padding: 16px 20px;
  background: #f5f7fa;
  border-radius: 12px;
  margin-top: 16px;
  font-size: 13px;
  color: #606266;
}

.pagination-container {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>