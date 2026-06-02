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
        <div class="loading-tip">Power Meter Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="power-meter-container">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Power Meter</h2>
        <p class="header-subtitle">Smart Power Monitoring | Real-time Energy Analytics</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Data
        </el-button>
        <el-button @click="refreshData">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Real-time Gauge Row -->
    <!-- Real-time Gauge Row -->
    <el-row :gutter="20" class="gauge-row">
      <el-col :xs="24" :sm="12" :md="6">
        <div class="gauge-card power">
          <div class="gauge-title">
        <span class="title-icon">
          <el-icon :size="16"><Lightning /></el-icon>
        </span>
            Power
          </div>
          <div ref="powerGaugeRef" class="gauge-container"></div>
          <div class="gauge-value">{{ realtimeData.power }} <span class="unit">kW</span></div>
          <div class="gauge-range">
            <span class="min">Min: 0</span>
            <span class="max">Max: 200</span>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="gauge-card current">
          <div class="gauge-title">
        <span class="title-icon">
          <el-icon :size="16"><Connection /></el-icon>
        </span>
            Current
          </div>
          <div ref="currentGaugeRef" class="gauge-container"></div>
          <div class="gauge-value">{{ realtimeData.current }} <span class="unit">A</span></div>
          <div class="gauge-range">
            <span class="min">Min: 0</span>
            <span class="max">Max: 500</span>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="gauge-card voltage">
          <div class="gauge-title">
        <span class="title-icon">
          <el-icon :size="16"><Histogram /></el-icon>
        </span>
            Voltage
          </div>
          <div ref="voltageGaugeRef" class="gauge-container"></div>
          <div class="gauge-value">{{ realtimeData.voltage }} <span class="unit">V</span></div>
          <div class="gauge-range">
            <span class="min">Min: 300</span>
            <span class="max">Max: 500</span>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="gauge-card pf">
          <div class="gauge-title">
        <span class="title-icon">
          <el-icon :size="16"><DataAnalysis /></el-icon>
        </span>
            Power Factor
          </div>
          <div ref="pfGaugeRef" class="gauge-container"></div>
          <div class="gauge-value">{{ realtimeData.powerFactor }} <span class="unit">pf</span></div>
          <div class="gauge-range">
            <span class="min">Poor: 0</span>
            <span class="max">Good: 1</span>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Meter Information Cards -->
    <el-row :gutter="20" class="info-row">
      <el-col :xs="24" :sm="12" :md="8">
        <div class="info-card">
          <div class="info-icon">
            <el-icon :size="24"><Document /></el-icon>
          </div>
          <div class="info-content">
            <div class="info-label">Meter ID</div>
            <div class="info-value">PM-{{ meterInfo.id }}</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8">
        <div class="info-card">
          <div class="info-icon">
            <el-icon :size="24"><Grid /></el-icon>
          </div>
          <div class="info-content">
            <div class="info-label">Model</div>
            <div class="info-value">{{ meterInfo.model }}</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8">
        <div class="info-card">
          <div class="info-icon">
            <el-icon :size="24"><Connection /></el-icon>
          </div>
          <div class="info-content">
            <div class="info-label">Modbus Address</div>
            <div class="info-value">{{ meterInfo.modbusAddress }}</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8">
        <div class="info-card">
          <div class="info-icon">
            <el-icon :size="24"><Location /></el-icon>
          </div>
          <div class="info-content">
            <div class="info-label">Location</div>
            <div class="info-value">{{ meterInfo.location }}</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8">
        <div class="info-card">
          <div class="info-icon">
            <el-icon :size="24"><Calendar /></el-icon>
          </div>
          <div class="info-content">
            <div class="info-label">Installation Date</div>
            <div class="info-value">{{ meterInfo.installDate }}</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8">
        <div class="info-card">
          <div class="info-icon">
            <el-icon :size="24"><Monitor /></el-icon>
          </div>
          <div class="info-content">
            <div class="info-label">Status</div>
            <div class="info-value">
              <el-tag :type="meterInfo.status === 'Online' ? 'success' : 'danger'" size="small">
                {{ meterInfo.status }}
              </el-tag>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Energy Summary Cards -->
    <el-row :gutter="20" class="energy-row">
      <el-col :xs="24" :sm="12" :md="6">
        <div class="energy-card">
          <div class="energy-icon active-power">
            <el-icon :size="24"><Lightning /></el-icon>
          </div>
          <div class="energy-details">
            <div class="energy-label">Active Power</div>
            <div class="energy-value">{{ realtimeData.activePower }} <span class="unit">kW</span></div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="energy-card">
          <div class="energy-icon reactive-power">
            <el-icon :size="24"><Connection /></el-icon>
          </div>
          <div class="energy-details">
            <div class="energy-label">Reactive Power</div>
            <div class="energy-value">{{ realtimeData.reactivePower }} <span class="unit">kVAR</span></div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="energy-card">
          <div class="energy-icon apparent-power">
            <el-icon :size="24"><Histogram /></el-icon>
          </div>
          <div class="energy-details">
            <div class="energy-label">Apparent Power</div>
            <div class="energy-value">{{ realtimeData.apparentPower }} <span class="unit">kVA</span></div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="energy-card">
          <div class="energy-icon frequency">
            <el-icon :size="24"><Timer /></el-icon>
          </div>
          <div class="energy-details">
            <div class="energy-label">Frequency</div>
            <div class="energy-value">{{ realtimeData.frequency }} <span class="unit">Hz</span></div>
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
              <span>Power Consumption Trend</span>
              <el-radio-group v-model="chartPeriod" size="small" @change="updateChartPeriod">
                <el-radio-button label="hour">Hourly</el-radio-button>
                <el-radio-button label="day">Daily</el-radio-button>
                <el-radio-button label="week">Weekly</el-radio-button>
                <el-radio-button label="month">Monthly</el-radio-button>
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
              <span>Energy Distribution</span>
            </div>
          </template>
          <div ref="pieChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Phase Details -->
    <el-card shadow="hover" class="phase-card">
      <template #header>
        <div class="card-header">
          <span>Phase Details (3-Phase 4-Wire)</span>
          <el-tag type="info">{{ phaseData.length }} Phases</el-tag>
        </div>
      </template>
      <el-table :data="phaseData" stripe border style="width: 100%">
        <el-table-column prop="phase" label="Phase" width="80">
          <template #default="{ row }">
            <span class="phase-badge" :class="row.phase.toLowerCase()">{{ row.phase }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="voltage" label="Voltage (V)" sortable>
          <template #default="{ row }">
            <span :class="getVoltageClass(row.voltage)">{{ row.voltage }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="current" label="Current (A)" sortable />
        <el-table-column prop="power" label="Power (kW)" sortable />
        <el-table-column prop="powerFactor" label="Power Factor" sortable />
        <el-table-column prop="thd" label="THD (%)" sortable>
          <template #default="{ row }">
            <span :class="getThdClass(row.thd)">{{ row.thd }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="Load" min-width="150">
          <template #default="{ row }">
            <el-progress
                :percentage="row.loadPercent"
                :color="row.loadPercent > 80 ? '#F56C6C' : (row.loadPercent > 60 ? '#E6A23C' : '#67C23A')"
                :stroke-width="8"
            />
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Energy Accumulation -->
    <el-row :gutter="20">
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" class="accumulation-card">
          <template #header>
            <div class="card-header">
              <span>Energy Accumulation</span>
            </div>
          </template>
          <div class="accumulation-grid">
            <div class="accumulation-item">
              <div class="accumulation-label">Today</div>
              <div class="accumulation-value">{{ accumulation.today }} <span class="unit">kWh</span></div>
              <div class="accumulation-change positive">+{{ accumulation.todayChange }}%</div>
            </div>
            <div class="accumulation-item">
              <div class="accumulation-label">This Week</div>
              <div class="accumulation-value">{{ accumulation.week }} <span class="unit">kWh</span></div>
              <div class="accumulation-change positive">+{{ accumulation.weekChange }}%</div>
            </div>
            <div class="accumulation-item">
              <div class="accumulation-label">This Month</div>
              <div class="accumulation-value">{{ accumulation.month }} <span class="unit">kWh</span></div>
              <div class="accumulation-change negative">{{ accumulation.monthChange }}%</div>
            </div>
            <div class="accumulation-item">
              <div class="accumulation-label">This Year</div>
              <div class="accumulation-value">{{ accumulation.year }} <span class="unit">kWh</span></div>
              <div class="accumulation-change positive">+{{ accumulation.yearChange }}%</div>
            </div>
          </div>
          <div class="accumulation-footer">
            <div class="footer-item">
              <span>Import: {{ accumulation.import }} kWh</span>
              <span>Export: {{ accumulation.export }} kWh</span>
            </div>
            <div class="footer-item">
              <span>Max Demand: {{ accumulation.maxDemand }} kW</span>
              <span>Peak Time: {{ accumulation.peakTime }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" class="tariff-card">
          <template #header>
            <div class="card-header">
              <span>Tariff & Cost Analysis</span>
            </div>
          </template>
          <div class="tariff-content">
            <div class="tariff-item">
              <div class="tariff-label">Current Tariff</div>
              <div class="tariff-value">$0.12 <span class="unit">/kWh</span></div>
            </div>
            <div class="tariff-item">
              <div class="tariff-label">Demand Charge</div>
              <div class="tariff-value">$8.50 <span class="unit">/kW</span></div>
            </div>
            <div class="tariff-item">
              <div class="tariff-label">Today's Cost</div>
              <div class="tariff-value">${{ cost.today }} <span class="unit">USD</span></div>
            </div>
            <div class="tariff-item">
              <div class="tariff-label">Month's Cost</div>
              <div class="tariff-value">${{ cost.month }} <span class="unit">USD</span></div>
            </div>
            <div class="tariff-item">
              <div class="tariff-label">Year's Cost</div>
              <div class="tariff-value">${{ cost.year }} <span class="unit">USD</span></div>
            </div>
            <div class="tariff-item">
              <div class="tariff-label">CO₂ Emission</div>
              <div class="tariff-value">{{ co2Emission }} <span class="unit">kg</span></div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Harmonics Table -->
    <el-card shadow="hover" class="harmonics-card">
      <template #header>
        <div class="card-header">
          <span>Harmonics Analysis (THD by Order)</span>
          <el-button text @click="refreshHarmonics">Refresh</el-button>
        </div>
      </template>
      <el-table :data="harmonicsData" stripe border size="small">
        <el-table-column prop="order" label="Harmonic Order" width="120" />
        <el-table-column prop="rPhase" label="R Phase (%)" sortable>
          <template #default="{ row }">
            <el-progress :percentage="row.rPhase" :stroke-width="6" :show-text="false" />
            <span>{{ row.rPhase }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="yPhase" label="Y Phase (%)" sortable>
          <template #default="{ row }">
            <el-progress :percentage="row.yPhase" :stroke-width="6" :show-text="false" />
            <span>{{ row.yPhase }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="bPhase" label="B Phase (%)" sortable>
          <template #default="{ row }">
            <el-progress :percentage="row.bPhase" :stroke-width="6" :show-text="false" />
            <span>{{ row.bPhase }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="limit" label="IEC Limit (%)" width="120" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="getHarmonicStatus(row)" size="small">
              {{ getHarmonicStatusText(row) }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Download,
  Refresh,
  Document,
  Grid,
  Connection,
  Location,
  Calendar,
  Monitor,
  Lightning,
  Histogram,
  Timer
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Initializing power meter...',
  'Reading Modbus data...',
  'Almost ready...'
]

// ==================== Data State ====================
const chartPeriod = ref('hour')

// Meter Info
const meterInfo = ref({
  id: 'PM-1024',
  model: 'Siemens PAC4200',
  modbusAddress: '01',
  location: 'Main Switchboard - Building A',
  installDate: '2023-06-15',
  status: 'Online'
})

// Realtime Data
const realtimeData = ref({
  power: 0,
  current: 0,
  voltage: 0,
  powerFactor: 0,
  activePower: 0,
  reactivePower: 0,
  apparentPower: 0,
  frequency: 0
})

// Phase Data
interface PhaseDetail {
  phase: string
  voltage: number
  current: number
  power: number
  powerFactor: number
  thd: number
  loadPercent: number
}

const phaseData = ref<PhaseDetail[]>([])

// Energy Accumulation
const accumulation = ref({
  today: 0,
  todayChange: 0,
  week: 0,
  weekChange: 0,
  month: 0,
  monthChange: 0,
  year: 0,
  yearChange: 0,
  import: 0,
  export: 0,
  maxDemand: 0,
  peakTime: ''
})

// Cost Analysis
const cost = ref({
  today: 0,
  month: 0,
  year: 0
})

const co2Emission = ref(0)

// Harmonics Data
interface Harmonic {
  order: string
  rPhase: number
  yPhase: number
  bPhase: number
  limit: number
}

const harmonicsData = ref<Harmonic[]>([])

// Generate mock data
const generateRealtimeData = () => {
  realtimeData.value = {
    power: parseFloat((Math.random() * 100 + 50).toFixed(1)),
    current: parseFloat((Math.random() * 300 + 150).toFixed(1)),
    voltage: parseFloat((395 + Math.random() * 15).toFixed(1)),
    powerFactor: parseFloat((0.85 + Math.random() * 0.1).toFixed(2)),
    activePower: parseFloat((Math.random() * 100 + 50).toFixed(1)),
    reactivePower: parseFloat((Math.random() * 40 + 10).toFixed(1)),
    apparentPower: parseFloat((Math.random() * 120 + 60).toFixed(1)),
    frequency: parseFloat((49.8 + Math.random() * 0.6).toFixed(1))
  }
}

const generatePhaseData = (): PhaseDetail[] => {
  const baseVoltage = 400
  const phases = ['R', 'Y', 'B']
  return phases.map(phase => {
    const voltage = baseVoltage + (Math.random() - 0.5) * 10
    const current = parseFloat((150 + Math.random() * 100).toFixed(1))
    const power = parseFloat((current * 0.23).toFixed(1))
    const powerFactor = parseFloat((0.85 + Math.random() * 0.1).toFixed(2))
    const loadPercent = parseFloat(((current / 250) * 100).toFixed(1))

    return {
      phase: phase,
      voltage: parseFloat(voltage.toFixed(1)),
      current: current,
      power: power,
      powerFactor: powerFactor,
      thd: parseFloat((1.5 + Math.random() * 3).toFixed(1)),
      loadPercent: loadPercent
    }
  })
}

const generateAccumulation = () => {
  accumulation.value = {
    today: parseFloat((Math.random() * 2000 + 1000).toFixed(1)),
    todayChange: parseFloat((Math.random() * 20 - 5).toFixed(1)),
    week: parseFloat((Math.random() * 15000 + 8000).toFixed(1)),
    weekChange: parseFloat((Math.random() * 15 - 3).toFixed(1)),
    month: parseFloat((Math.random() * 60000 + 30000).toFixed(1)),
    monthChange: parseFloat((Math.random() * 10 - 8).toFixed(1)),
    year: parseFloat((Math.random() * 500000 + 300000).toFixed(1)),
    yearChange: parseFloat((Math.random() * 12 - 2).toFixed(1)),
    import: parseFloat((Math.random() * 200000 + 100000).toFixed(1)),
    export: parseFloat((Math.random() * 50000 + 10000).toFixed(1)),
    maxDemand: parseFloat((250 + Math.random() * 100).toFixed(1)),
    peakTime: '14:30 - 15:00'
  }

  cost.value = {
    today: parseFloat((accumulation.value.today * 0.12).toFixed(1)),
    month: parseFloat((accumulation.value.month * 0.12).toFixed(0)),
    year: parseFloat((accumulation.value.year * 0.12).toFixed(0))
  }

  co2Emission.value = Math.round(accumulation.value.year * 0.4)
}

const generateHarmonics = (): Harmonic[] => {
  return [
    { order: '3rd', rPhase: parseFloat((1.2 + Math.random() * 1).toFixed(1)), yPhase: parseFloat((1.1 + Math.random() * 1).toFixed(1)), bPhase: parseFloat((1.3 + Math.random() * 1).toFixed(1)), limit: 5.0 },
    { order: '5th', rPhase: parseFloat((2.5 + Math.random() * 1.5).toFixed(1)), yPhase: parseFloat((2.3 + Math.random() * 1.5).toFixed(1)), bPhase: parseFloat((2.6 + Math.random() * 1.5).toFixed(1)), limit: 6.0 },
    { order: '7th', rPhase: parseFloat((1.8 + Math.random() * 1).toFixed(1)), yPhase: parseFloat((1.6 + Math.random() * 1).toFixed(1)), bPhase: parseFloat((1.9 + Math.random() * 1).toFixed(1)), limit: 5.0 },
    { order: '9th', rPhase: parseFloat((0.8 + Math.random() * 0.8).toFixed(1)), yPhase: parseFloat((0.7 + Math.random() * 0.8).toFixed(1)), bPhase: parseFloat((0.9 + Math.random() * 0.8).toFixed(1)), limit: 3.0 },
    { order: '11th', rPhase: parseFloat((1.2 + Math.random() * 0.8).toFixed(1)), yPhase: parseFloat((1.1 + Math.random() * 0.8).toFixed(1)), bPhase: parseFloat((1.3 + Math.random() * 0.8).toFixed(1)), limit: 3.5 },
    { order: '13th', rPhase: parseFloat((0.6 + Math.random() * 0.6).toFixed(1)), yPhase: parseFloat((0.5 + Math.random() * 0.6).toFixed(1)), bPhase: parseFloat((0.7 + Math.random() * 0.6).toFixed(1)), limit: 3.0 }
  ]
}

// ==================== Gauge Charts ====================
const powerGaugeRef = ref<HTMLElement>()
const currentGaugeRef = ref<HTMLElement>()
const voltageGaugeRef = ref<HTMLElement>()
const pfGaugeRef = ref<HTMLElement>()

let powerGauge: echarts.ECharts | null = null
let currentGauge: echarts.ECharts | null = null
let voltageGauge: echarts.ECharts | null = null
let pfGauge: echarts.ECharts | null = null

const initGauges = () => {
  nextTick(() => {
    const gaugeOption = (value: number, min: number, max: number, name: string, color: string[]) => ({
      series: [{
        type: 'gauge',
        center: ['50%', '50%'],
        radius: '70%',
        min: min,
        max: max,
        endAngle: 270,
        progress: { show: true, width: 12, itemStyle: { color: color } },
        axisLine: { lineStyle: { width: 12, color: [[1, '#e4e7ed']] } },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        pointer: { show: false },
        detail: { show: false },
        title: { show: false },
        data: [{ value: value, name: name }]
      }]
    })

    if (powerGaugeRef.value) {
      if (powerGauge) powerGauge.dispose()
      powerGauge = echarts.init(powerGaugeRef.value)
      powerGauge.setOption(gaugeOption(realtimeData.value.power, 0, 200, 'Power', ['#409EFF']))
    }

    if (currentGaugeRef.value) {
      if (currentGauge) currentGauge.dispose()
      currentGauge = echarts.init(currentGaugeRef.value)
      currentGauge.setOption(gaugeOption(realtimeData.value.current, 0, 500, 'Current', ['#67C23A']))
    }

    if (voltageGaugeRef.value) {
      if (voltageGauge) voltageGauge.dispose()
      voltageGauge = echarts.init(voltageGaugeRef.value)
      voltageGauge.setOption(gaugeOption(realtimeData.value.voltage, 300, 500, 'Voltage', ['#E6A23C']))
    }

    if (pfGaugeRef.value) {
      if (pfGauge) pfGauge.dispose()
      pfGauge = echarts.init(pfGaugeRef.value)
      pfGauge.setOption(gaugeOption(realtimeData.value.powerFactor * 100, 0, 100, 'Power Factor', ['#F56C6C']))
    }
  })
}

const updateGauges = () => {
  const updateGauge = (gauge: echarts.ECharts | null, value: number) => {
    if (gauge) {
      gauge.setOption({ series: [{ data: [{ value: value }] }] })
    }
  }

  updateGauge(powerGauge, realtimeData.value.power)
  updateGauge(currentGauge, realtimeData.value.current)
  updateGauge(voltageGauge, realtimeData.value.voltage)
  updateGauge(pfGauge, realtimeData.value.powerFactor * 100)
}

// ==================== Chart Functions ====================
const trendChartRef = ref<HTMLElement>()
const pieChartRef = ref<HTMLElement>()
let trendChart: echarts.ECharts | null = null
let pieChart: echarts.ECharts | null = null

const initCharts = () => {
  nextTick(() => {
    if (trendChartRef.value) {
      if (trendChart) trendChart.dispose()
      trendChart = echarts.init(trendChartRef.value)
      updateTrendChart()
    }

    if (pieChartRef.value) {
      if (pieChart) pieChart.dispose()
      pieChart = echarts.init(pieChartRef.value)
      updatePieChart()
    }
  })
}

const updateTrendChart = () => {
  let powerData: number[] = []
  let energyData: number[] = []
  let xAxisData: string[] = []

  if (chartPeriod.value === 'hour') {
    xAxisData = Array.from({ length: 24 }, (_, i) => `${i}:00`)
    powerData = Array.from({ length: 24 }, () => parseFloat((Math.random() * 80 + 40).toFixed(1)))
    energyData = Array.from({ length: 24 }, () => parseFloat((Math.random() * 50 + 20).toFixed(1)))
  } else if (chartPeriod.value === 'day') {
    xAxisData = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    powerData = [65, 72, 68, 78, 85, 75, 62]
    energyData = [42, 48, 45, 52, 58, 50, 40]
  } else if (chartPeriod.value === 'week') {
    xAxisData = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
    powerData = [68, 72, 70, 75]
    energyData = [45, 48, 46, 50]
  } else {
    xAxisData = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    powerData = [62, 65, 68, 70, 75, 80, 82, 78, 72, 68, 65, 60]
    energyData = [40, 42, 45, 48, 52, 56, 58, 54, 48, 44, 42, 38]
  }

  trendChart?.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Power (kW)', 'Energy (kWh)'] },
    xAxis: { type: 'category', data: xAxisData },
    yAxis: [{ type: 'value', name: 'Power (kW)' }, { type: 'value', name: 'Energy (kWh)' }],
    series: [
      {
        name: 'Power (kW)',
        type: 'line',
        data: powerData,
        smooth: true,
        lineStyle: { color: '#409EFF', width: 3 },
        areaStyle: { opacity: 0.1 },
        symbol: 'circle',
        symbolSize: 6
      },
      {
        name: 'Energy (kWh)',
        type: 'bar',
        data: energyData,
        itemStyle: { borderRadius: [4, 4, 0, 0], color: '#67C23A' }
      }
    ]
  })
}

const updatePieChart = () => {
  const total = phaseData.value.reduce((sum, p) => sum + p.power, 0)

  pieChart?.setOption({
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: '55%',
      data: phaseData.value.map(p => ({
        name: `${p.phase} Phase`,
        value: p.power,
        itemStyle: { color: p.phase === 'R' ? '#F56C6C' : (p.phase === 'Y' ? '#E6A23C' : '#409EFF') }
      })),
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  })
}

const updateChartPeriod = () => {
  updateTrendChart()
}

// ==================== Helper Functions ====================
const getVoltageClass = (voltage: number) => {
  if (voltage >= 380 && voltage <= 420) return ''
  return 'warning-text'
}

const getThdClass = (thd: number) => {
  if (thd < 3) return ''
  if (thd < 5) return 'warning-text'
  return 'danger-text'
}

const getHarmonicStatus = (row: Harmonic) => {
  const maxThd = Math.max(row.rPhase, row.yPhase, row.bPhase)
  if (maxThd < row.limit * 0.7) return 'success'
  if (maxThd < row.limit) return 'warning'
  return 'danger'
}

const getHarmonicStatusText = (row: Harmonic) => {
  const maxThd = Math.max(row.rPhase, row.yPhase, row.bPhase)
  if (maxThd < row.limit * 0.7) return 'Good'
  if (maxThd < row.limit) return 'Marginal'
  return 'Exceed'
}

// ==================== Actions ====================
const refreshData = () => {
  generateRealtimeData()
  phaseData.value = generatePhaseData()
  generateAccumulation()
  harmonicsData.value = generateHarmonics()
  updateGauges()
  updateTrendChart()
  updatePieChart()
  ElMessage.success('Data refreshed')
}

const refreshHarmonics = () => {
  harmonicsData.value = generateHarmonics()
  ElMessage.success('Harmonics data refreshed')
}

const handleExport = () => {
  ElMessage.success('Data export started')
}

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
      generateRealtimeData()
      phaseData.value = generatePhaseData()
      generateAccumulation()
      harmonicsData.value = generateHarmonics()
      initGauges()
      initCharts()

      // Simulate real-time updates
      setInterval(() => {
        if (isLoaded.value) {
          generateRealtimeData()
          updateGauges()
        }
      }, 5000)
    }, 400)
  }, 2000)
})

watch([trendChartRef, pieChartRef], () => {
  window.addEventListener('resize', () => {
    trendChart?.resize()
    pieChart?.resize()
    powerGauge?.resize()
    currentGauge?.resize()
    voltageGauge?.resize()
    pfGauge?.resize()
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
.power-meter-container {
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

/* Gauge Cards */
.gauge-row {
  margin-bottom: 20px;
}

.gauge-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: all 0.3s ease;
}

.gauge-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}

.gauge-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 12px;
}

.gauge-container {
  width: 100%;
  height: 120px;
}

.gauge-value {
  font-size: 24px;
  font-weight: 700;
  color: #1f2f3d;
  margin-top: 8px;
}

.gauge-value .unit {
  font-size: 12px;
  font-weight: normal;
  color: #909399;
}

/* Info Cards */
.info-row {
  margin-bottom: 20px;
}

.info-card {
  background: white;
  border-radius: 12px;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.info-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: rgba(64, 158, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #409EFF;
}

.info-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.info-value {
  font-size: 14px;
  font-weight: 600;
  color: #1f2f3d;
}

/* Energy Cards */
.energy-row {
  margin-bottom: 20px;
}

.energy-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: all 0.3s ease;
}

.energy-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}

.energy-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.energy-icon.active-power { background: rgba(64, 158, 255, 0.1); color: #409EFF; }
.energy-icon.reactive-power { background: rgba(230, 162, 60, 0.1); color: #E6A23C; }
.energy-icon.apparent-power { background: rgba(103, 194, 58, 0.1); color: #67C23A; }
.energy-icon.frequency { background: rgba(144, 147, 153, 0.1); color: #909399; }

.energy-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 4px;
}

.energy-value {
  font-size: 20px;
  font-weight: 700;
  color: #1f2f3d;
}

.energy-value .unit {
  font-size: 11px;
  font-weight: normal;
  color: #909399;
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

/* Phase Card */
.phase-card {
  border-radius: 16px;
  margin-bottom: 20px;
}

.phase-badge {
  display: inline-block;
  width: 32px;
  height: 32px;
  line-height: 32px;
  text-align: center;
  border-radius: 8px;
  font-weight: 600;
}

.phase-badge.r { background: rgba(245, 108, 108, 0.15); color: #F56C6C; }
.phase-badge.y { background: rgba(230, 162, 60, 0.15); color: #E6A23C; }
.phase-badge.b { background: rgba(64, 158, 255, 0.15); color: #409EFF; }

/* Accumulation Card */
.accumulation-card, .tariff-card {
  border-radius: 16px;
  margin-bottom: 20px;
}

.accumulation-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  padding: 10px;
}

.accumulation-item {
  text-align: center;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 12px;
}

.accumulation-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.accumulation-value {
  font-size: 24px;
  font-weight: 700;
  color: #409EFF;
}

.accumulation-value .unit {
  font-size: 11px;
  font-weight: normal;
  color: #909399;
}

.accumulation-change {
  font-size: 12px;
  margin-top: 6px;
}

.accumulation-change.positive { color: #67C23A; }
.accumulation-change.negative { color: #F56C6C; }

.accumulation-footer {
  margin-top: 16px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 12px;
}

.footer-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 13px;
  color: #606266;
}

/* Tariff Card */
.tariff-content {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.tariff-item {
  text-align: center;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 12px;
}

.tariff-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 6px;
}

.tariff-value {
  font-size: 18px;
  font-weight: 600;
  color: #1f2f3d;
}

.tariff-value .unit {
  font-size: 11px;
  font-weight: normal;
  color: #909399;
}

/* Harmonics Card */
.harmonics-card {
  border-radius: 16px;
}

.warning-text { color: #E6A23C; font-weight: 500; }
.danger-text { color: #F56C6C; font-weight: 500; }

.gauge-card:nth-child(1) .gauge-value { color: #409EFF; }  /* 功率 - 蓝色 */
.gauge-card:nth-child(2) .gauge-value { color: #67C23A; }  /* 电流 - 绿色 */
.gauge-card:nth-child(3) .gauge-value { color: #E6A23C; }  /* 电压 - 橙色 */
.gauge-card:nth-child(4) .gauge-value { color: #F56C6C; }  /* 功率因数 - 红色 */

/* Gauge Cards */
.gauge-row {
  margin-bottom: 20px;
}

.gauge-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.gauge-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
}

.gauge-card.power::before { background: linear-gradient(90deg, #409EFF, #66b1ff); }
.gauge-card.current::before { background: linear-gradient(90deg, #67C23A, #85ce61); }
.gauge-card.voltage::before { background: linear-gradient(90deg, #E6A23C, #f5d7b3); }
.gauge-card.pf::before { background: linear-gradient(90deg, #F56C6C, #f89898); }

.gauge-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(0,0,0,0.12);
}

.gauge-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.gauge-title .title-icon {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.gauge-card.power .title-icon { background: rgba(64, 158, 255, 0.15); color: #409EFF; }
.gauge-card.current .title-icon { background: rgba(103, 194, 58, 0.15); color: #67C23A; }
.gauge-card.voltage .title-icon { background: rgba(230, 162, 60, 0.15); color: #E6A23C; }
.gauge-card.pf .title-icon { background: rgba(245, 108, 108, 0.15); color: #F56C6C; }

.gauge-container {
  width: 100%;
  height: 140px;
}

.gauge-value {
  font-size: 28px;
  font-weight: 700;
  margin-top: 8px;
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 4px;
}

.gauge-card.power .gauge-value { color: #409EFF; }
.gauge-card.current .gauge-value { color: #67C23A; }
.gauge-card.voltage .gauge-value { color: #E6A23C; }
.gauge-card.pf .gauge-value { color: #F56C6C; }

.gauge-value .unit {
  font-size: 13px;
  font-weight: normal;
  color: #909399;
}

.gauge-range {
  font-size: 11px;
  color: #c0c4cc;
  margin-top: 6px;
  display: flex;
  justify-content: center;
  gap: 12px;
}

.gauge-range span.min { color: #F56C6C; }
.gauge-range span.max { color: #67C23A; }
</style>