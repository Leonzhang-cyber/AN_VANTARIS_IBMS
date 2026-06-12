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
        <div class="loading-tip">Digital Twin - Scenario Simulation</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="scenario-simulation-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>Scenario Simulation</h1>
        <p>Run what-if scenarios to predict outcomes and optimize building operations</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="runSimulation" :loading="isSimulating">
          <el-icon><VideoPlay /></el-icon>
          Run Simulation
        </el-button>
        <el-button @click="exportResults">
          <el-icon><Download /></el-icon>
          Export Results
        </el-button>
        <el-button @click="resetSimulation">
          <el-icon><RefreshLeft /></el-icon>
          Reset
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon primary-bg">
            <el-icon><DataAnalysis /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.scenariosRun }}</div>
            <div class="stat-label">Scenarios Run</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon success-bg">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">+{{ stats.potentialSavings }}%</div>
            <div class="stat-label">Potential Savings</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon warning-bg">
            <el-icon><Timer /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.avgSimTime }}s</div>
            <div class="stat-label">Avg Simulation Time</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon info-bg">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.accuracy }}%</div>
            <div class="stat-label">Model Accuracy</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Main Content Row -->
    <el-row :gutter="20">
      <!-- Scenario Configuration Panel -->
      <el-col :xs="24" :lg="10">
        <div class="config-card">
          <div class="card-header">
            <h3>Scenario Configuration</h3>
            <el-tag :type="simulationStatus === 'running' ? 'warning' : simulationStatus === 'completed' ? 'success' : 'info'">
              {{ simulationStatus === 'idle' ? 'Ready' : simulationStatus === 'running' ? 'Running...' : 'Completed' }}
            </el-tag>
          </div>

          <!-- Preset Scenarios -->
          <div class="preset-section">
            <label>Preset Scenarios</label>
            <div class="preset-buttons">
              <el-button
                  v-for="preset in presets"
                  :key="preset.id"
                  :type="selectedPreset === preset.id ? 'primary' : 'default'"
                  size="small"
                  @click="loadPreset(preset)"
              >
                {{ preset.name }}
              </el-button>
            </div>
          </div>

          <el-divider />

          <!-- Simulation Parameters -->
          <el-form :model="params" label-width="140px" class="params-form">
            <el-form-item label="Simulation Duration">
              <el-slider v-model="params.duration" :min="1" :max="168" :step="1" />
              <span class="param-hint">{{ params.duration }} hours ({{ Math.floor(params.duration / 24) }} days)</span>
            </el-form-item>

            <el-form-item label="HVAC Setpoint">
              <el-slider v-model="params.hvacSetpoint" :min="18" :max="26" :step="0.5" />
              <span class="param-hint">{{ params.hvacSetpoint }}°C</span>
            </el-form-item>

            <el-form-item label="Lighting Level">
              <el-slider v-model="params.lightingLevel" :min="0" :max="100" :step="5" />
              <span class="param-hint">{{ params.lightingLevel }}%</span>
            </el-form-item>

            <el-form-item label="Equipment Schedule">
              <el-select v-model="params.equipmentSchedule" style="width: 100%">
                <el-option label="24/7 Operation" value="24_7" />
                <el-option label="Business Hours (8-18)" value="business" />
                <el-option label="Optimized Schedule" value="optimized" />
                <el-option label="Custom Schedule" value="custom" />
              </el-select>
            </el-form-item>

            <el-form-item label="Occupancy Level">
              <el-slider v-model="params.occupancy" :min="0" :max="100" :step="5" />
              <span class="param-hint">{{ params.occupancy }}% of capacity</span>
            </el-form-item>

            <el-form-item label="External Temperature">
              <el-slider v-model="params.externalTemp" :min="-10" :max="40" :step="1" />
              <span class="param-hint">{{ params.externalTemp }}°C</span>
            </el-form-item>

            <el-form-item label="Energy Price">
              <el-slider v-model="params.energyPrice" :min="0.05" :max="0.5" :step="0.01" :format-tooltip="(val) => `$${val}/kWh`" />
              <span class="param-hint">${{ params.energyPrice }}/kWh</span>
            </el-form-item>

            <el-form-item label="Simulation Mode">
              <el-radio-group v-model="params.mode">
                <el-radio value="real-time">Real-Time</el-radio>
                <el-radio value="accelerated">Accelerated (10x)</el-radio>
                <el-radio value="batch">Batch Analysis</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-form>

          <el-divider />

          <!-- Run Button with Progress -->
          <div class="run-section">
            <el-button
                type="primary"
                size="large"
                @click="runSimulation"
                :loading="isSimulating"
                :disabled="simulationStatus === 'running'"
                style="width: 100%"
            >
              <el-icon><VideoPlay /></el-icon>
              {{ isSimulating ? 'Simulating...' : 'Run Simulation' }}
            </el-button>
            <el-progress
                v-if="isSimulating"
                :percentage="simulationProgress"
                :status="simulationProgress === 100 ? 'success' : undefined"
                style="margin-top: 12px"
            />
          </div>
        </div>
      </el-col>

      <!-- Simulation Visualization & Results -->
      <el-col :xs="24" :lg="14">
        <div class="visualization-card">
          <div class="card-header">
            <h3>Simulation Visualization</h3>
            <div class="view-controls">
              <el-radio-group v-model="viewType" size="small">
                <el-radio-button value="3d">3D View</el-radio-button>
                <el-radio-button value="chart">Chart View</el-radio-button>
                <el-radio-button value="comparison">Comparison</el-radio-button>
              </el-radio-group>
            </div>
          </div>

          <!-- 3D View -->
          <div v-if="viewType === '3d'" class="viewer-container" ref="viewerContainerRef">
            <canvas ref="viewerCanvasRef" class="viewer-canvas"></canvas>
            <div v-if="isSimulating" class="simulation-overlay">
              <div class="simulation-status">Simulating Scenario...</div>
            </div>
          </div>

          <!-- Chart View -->
          <div v-if="viewType === 'chart'" class="chart-view">
            <div class="chart-tabs">
              <el-tabs v-model="activeChartTab">
                <el-tab-pane label="Energy Consumption" name="energy" />
                <el-tab-pane label="Temperature Profile" name="temperature" />
                <el-tab-pane label="Cost Analysis" name="cost" />
              </el-tabs>
            </div>
            <div ref="simChartRef" class="sim-chart-container"></div>
          </div>

          <!-- Comparison View -->
          <div v-if="viewType === 'comparison'" class="comparison-view">
            <div class="comparison-header">
              <span>Baseline vs Optimized</span>
              <el-select v-model="comparisonMetric" size="small" style="width: 150px">
                <el-option label="Energy (kWh)" value="energy" />
                <el-option label="Cost ($)" value="cost" />
                <el-option label="CO2 (kg)" value="co2" />
              </el-select>
            </div>
            <div ref="comparisonChartRef" class="comparison-chart-container"></div>
          </div>

          <!-- Results Summary -->
          <div class="results-summary" v-if="lastResults">
            <div class="summary-header">
              <h4>Simulation Results</h4>
              <el-tag type="success">{{ lastResults.scenarioName }}</el-tag>
            </div>
            <el-row :gutter="16">
              <el-col :span="8">
                <div class="result-card">
                  <div class="result-value">{{ lastResults.energyConsumption }}<span class="result-unit">kWh</span></div>
                  <div class="result-label">Total Energy</div>
                  <div class="result-delta" :class="lastResults.energyDelta < 0 ? 'positive' : 'negative'">
                    {{ lastResults.energyDelta > 0 ? '+' : '' }}{{ lastResults.energyDelta }}% vs baseline
                  </div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="result-card">
                  <div class="result-value">${{ lastResults.operatingCost }}<span class="result-unit">k</span></div>
                  <div class="result-label">Operating Cost</div>
                  <div class="result-delta" :class="lastResults.costDelta < 0 ? 'positive' : 'negative'">
                    {{ lastResults.costDelta > 0 ? '+' : '' }}{{ lastResults.costDelta }}% vs baseline
                  </div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="result-card">
                  <div class="result-value">{{ lastResults.co2Emissions }}<span class="result-unit">tons</span></div>
                  <div class="result-label">CO₂ Emissions</div>
                  <div class="result-delta" :class="lastResults.co2Delta < 0 ? 'positive' : 'negative'">
                    {{ lastResults.co2Delta > 0 ? '+' : '' }}{{ lastResults.co2Delta }}% vs baseline
                  </div>
                </div>
              </el-col>
            </el-row>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Historical Simulations -->
    <div class="history-card">
      <div class="card-header">
        <h3>Recent Simulations</h3>
        <el-button size="small" @click="clearHistory">Clear History</el-button>
      </div>
      <el-table :data="simulationHistory" stripe style="width: 100%">
        <el-table-column prop="timestamp" label="Date & Time" width="180">
          <template #default="{ row }">
            {{ formatFullTimestamp(row.timestamp) }}
          </template>
        </el-table-column>
        <el-table-column prop="scenarioName" label="Scenario" min-width="150" />
        <el-table-column prop="energyConsumption" label="Energy (kWh)" width="120" />
        <el-table-column prop="operatingCost" label="Cost ($k)" width="100" />
        <el-table-column prop="co2Emissions" label="CO₂ (tons)" width="100" />
        <el-table-column prop="savings" label="Savings" width="100">
          <template #default="{ row }">
            <span :class="row.savings > 0 ? 'positive' : 'negative'">
              {{ row.savings > 0 ? '+' : '' }}{{ row.savings }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="100">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="reloadSimulation(row)">
              Reload
            </el-button>
            <el-button link type="danger" size="small" @click="deleteHistoryItem(row)">
              Delete
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div v-if="simulationHistory.length === 0" class="no-history">
        <el-empty description="No simulation history" :image-size="80" />
      </div>
    </div>

    <!-- Compare Dialog -->
    <el-dialog v-model="compareDialog.visible" title="Compare Scenarios" width="800px">
      <div ref="compareChartRef" class="compare-chart-container"></div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  VideoPlay,
  Download,
  RefreshLeft,
  DataAnalysis,
  TrendCharts,
  Timer,
  CircleCheck
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const isSimulating = ref(false)
const simulationProgress = ref(0)
const simulationStatus = ref<'idle' | 'running' | 'completed'>('idle')
const viewType = ref<'3d' | 'chart' | 'comparison'>('3d')
const activeChartTab = ref('energy')
const comparisonMetric = ref('energy')
const selectedPreset = ref('')

const loadingMessages = [
  'Preparing...',
  'Loading simulation engine...',
  'Initializing digital twin...',
  'Almost ready...'
]

// ==================== Type Definitions ====================
interface SimulationParams {
  duration: number
  hvacSetpoint: number
  lightingLevel: number
  equipmentSchedule: string
  occupancy: number
  externalTemp: number
  energyPrice: number
  mode: string
}

interface SimulationResult {
  id: string
  scenarioName: string
  timestamp: Date
  energyConsumption: number
  operatingCost: number
  co2Emissions: number
  energyDelta: number
  costDelta: number
  co2Delta: number
  savings: number
  params: SimulationParams
}

interface Preset {
  id: string
  name: string
  description: string
  params: SimulationParams
}

// ==================== 预设场景 ====================
const presets: Preset[] = [
  {
    id: 'baseline',
    name: 'Baseline',
    description: 'Current operating conditions',
    params: {
      duration: 168,
      hvacSetpoint: 22,
      lightingLevel: 80,
      equipmentSchedule: '24_7',
      occupancy: 70,
      externalTemp: 25,
      energyPrice: 0.12,
      mode: 'real-time'
    }
  },
  {
    id: 'energy_saving',
    name: 'Energy Saving',
    description: 'Optimized for minimal energy use',
    params: {
      duration: 168,
      hvacSetpoint: 24,
      lightingLevel: 40,
      equipmentSchedule: 'optimized',
      occupancy: 70,
      externalTemp: 25,
      energyPrice: 0.12,
      mode: 'accelerated'
    }
  },
  {
    id: 'peak_load',
    name: 'Peak Load',
    description: 'High occupancy summer scenario',
    params: {
      duration: 24,
      hvacSetpoint: 20,
      lightingLevel: 90,
      equipmentSchedule: '24_7',
      occupancy: 95,
      externalTemp: 35,
      energyPrice: 0.25,
      mode: 'real-time'
    }
  },
  {
    id: 'winter',
    name: 'Winter Operation',
    description: 'Cold climate optimization',
    params: {
      duration: 168,
      hvacSetpoint: 20,
      lightingLevel: 70,
      equipmentSchedule: 'business',
      occupancy: 60,
      externalTemp: -5,
      energyPrice: 0.10,
      mode: 'real-time'
    }
  },
  {
    id: 'carbon_neutral',
    name: 'Carbon Neutral',
    description: 'Minimize carbon footprint',
    params: {
      duration: 168,
      hvacSetpoint: 23,
      lightingLevel: 50,
      equipmentSchedule: 'optimized',
      occupancy: 65,
      externalTemp: 22,
      energyPrice: 0.15,
      mode: 'accelerated'
    }
  }
]

// ==================== 响应式状态 ====================
const params = reactive<SimulationParams>({
  duration: 168,
  hvacSetpoint: 22,
  lightingLevel: 80,
  equipmentSchedule: '24_7',
  occupancy: 70,
  externalTemp: 25,
  energyPrice: 0.12,
  mode: 'real-time'
})

const lastResults = ref<SimulationResult | null>(null)
const simulationHistory = ref<SimulationResult[]>([])
const baselineResult = ref<SimulationResult | null>(null)

const viewerCanvasRef = ref<HTMLCanvasElement | null>(null)
const viewerContainerRef = ref<HTMLDivElement | null>(null)
const simChartRef = ref<HTMLElement | null>(null)
const comparisonChartRef = ref<HTMLElement | null>(null)
const compareChartRef = ref<HTMLElement | null>(null)

let animationFrameId: number | null = null
let simChart: echarts.ECharts | null = null
let comparisonChart: echarts.ECharts | null = null
let compareChart: echarts.ECharts | null = null

const stats = reactive({
  scenariosRun: 0,
  potentialSavings: 0,
  avgSimTime: 2.4,
  accuracy: 94.7
})

const compareDialog = reactive({
  visible: false,
  scenarios: [] as SimulationResult[]
})

// ==================== 辅助函数 ====================
const formatFullTimestamp = (date: Date) => {
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// ==================== 模拟计算引擎 ====================
const calculateSimulation = (simParams: SimulationParams, scenarioName: string): SimulationResult => {
  // Simulate energy consumption calculation
  const baseEnergy = 25000 // kWh per week baseline
  const hvacFactor = (simParams.hvacSetpoint - 22) * 0.03
  const lightingFactor = (simParams.lightingLevel - 80) * 0.002
  const occupancyFactor = (simParams.occupancy - 70) * 0.005
  const tempFactor = (simParams.externalTemp - 25) * 0.01
  const scheduleFactor = simParams.equipmentSchedule === 'optimized' ? -0.15 :
      simParams.equipmentSchedule === 'business' ? -0.1 : 0

  const durationFactor = simParams.duration / 168
  const energyMultiplier = 1 + hvacFactor + lightingFactor + occupancyFactor + tempFactor + scheduleFactor
  let energyConsumption = Math.floor(baseEnergy * energyMultiplier * durationFactor)

  // Ensure reasonable bounds
  energyConsumption = Math.max(5000, Math.min(60000, energyConsumption))

  const operatingCost = (energyConsumption * simParams.energyPrice) / 1000
  const co2Emissions = Math.floor(energyConsumption * 0.0004)

  // Calculate deltas against baseline
  let energyDelta = 0
  let costDelta = 0
  let co2Delta = 0
  let savings = 0

  if (baselineResult.value) {
    energyDelta = Math.round(((energyConsumption - baselineResult.value.energyConsumption) / baselineResult.value.energyConsumption) * 100)
    costDelta = Math.round(((operatingCost - baselineResult.value.operatingCost) / baselineResult.value.operatingCost) * 100)
    co2Delta = Math.round(((co2Emissions - baselineResult.value.co2Emissions) / baselineResult.value.co2Emissions) * 100)
    savings = -energyDelta
  }

  return {
    id: `sim-${Date.now()}`,
    scenarioName: scenarioName,
    timestamp: new Date(),
    energyConsumption: energyConsumption,
    operatingCost: parseFloat(operatingCost.toFixed(1)),
    co2Emissions: co2Emissions,
    energyDelta: energyDelta,
    costDelta: costDelta,
    co2Delta: co2Delta,
    savings: savings,
    params: { ...simParams }
  }
}

// ==================== 3D 场景绘制 ====================
const draw3DScene = () => {
  const canvas = viewerCanvasRef.value
  const container = viewerContainerRef.value
  if (!canvas || !container) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const width = container.clientWidth
  const height = 400
  canvas.width = width
  canvas.height = height

  // Background based on simulation status
  const gradient = ctx.createLinearGradient(0, 0, 0, height)
  if (isSimulating.value) {
    gradient.addColorStop(0, '#1a1a2e')
    gradient.addColorStop(1, '#16213e')
  } else {
    gradient.addColorStop(0, '#0f172a')
    gradient.addColorStop(1, '#1e293b')
  }
  ctx.fillStyle = gradient
  ctx.fillRect(0, 0, width, height)

  // Draw building outline
  const centerX = width / 2
  const centerY = height / 2 - 20

  // Building body
  ctx.fillStyle = 'rgba(64, 158, 255, 0.15)'
  ctx.fillRect(centerX - 100, centerY - 120, 200, 240)
  ctx.strokeStyle = '#409eff'
  ctx.lineWidth = 2
  ctx.strokeRect(centerX - 100, centerY - 120, 200, 240)

  // Draw floors
  for (let i = 0; i < 6; i++) {
    const y = centerY - 100 + i * 30
    ctx.beginPath()
    ctx.moveTo(centerX - 100, y)
    ctx.lineTo(centerX + 100, y)
    ctx.strokeStyle = 'rgba(100, 150, 255, 0.3)'
    ctx.stroke()
  }

  // Draw heat/cool indicators based on parameters
  const tempColor = params.hvacSetpoint > 23 ? '#f56c6c' : params.hvacSetpoint < 20 ? '#409eff' : '#67c23a'
  ctx.fillStyle = tempColor
  ctx.fillRect(centerX - 95, centerY - 115, 190, 10)

  // Draw occupancy dots
  const occupancyCount = Math.floor(params.occupancy / 10)
  for (let i = 0; i < occupancyCount; i++) {
    ctx.fillStyle = '#e6a23c'
    ctx.beginPath()
    ctx.arc(centerX - 70 + (i * 15), centerY + 40, 3, 0, Math.PI * 2)
    ctx.fill()
  }

  // Animation effects during simulation
  if (isSimulating.value) {
    const pulse = (Date.now() % 1000) / 1000
    ctx.strokeStyle = `rgba(64, 158, 255, ${0.5 + pulse * 0.5})`
    ctx.lineWidth = 3
    ctx.strokeRect(centerX - 102, centerY - 122, 204, 244)
  }

  // Draw parameter indicators
  ctx.fillStyle = 'white'
  ctx.font = '10px Arial'
  ctx.fillText(`HVAC: ${params.hvacSetpoint}°C`, centerX - 90, centerY + 80)
  ctx.fillText(`Lighting: ${params.lightingLevel}%`, centerX - 90, centerY + 95)
  ctx.fillText(`Occupancy: ${params.occupancy}%`, centerX - 90, centerY + 110)
  ctx.fillText(`External: ${params.externalTemp}°C`, centerX + 20, centerY + 80)
  ctx.fillText(`Duration: ${params.duration}h`, centerX + 20, centerY + 95)
}

const startRenderLoop = () => {
  const render = () => {
    draw3DScene()
    animationFrameId = requestAnimationFrame(render)
  }
  render()
}

// ==================== 图表渲染 ====================
const renderSimChart = () => {
  if (!simChartRef.value) return
  if (simChart) simChart.dispose()

  simChart = echarts.init(simChartRef.value)

  const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)
  let data: number[] = []

  if (activeChartTab.value === 'energy') {
    data = Array.from({ length: 24 }, () => 40 + Math.random() * 60)
    simChart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: hours, name: 'Hour' },
      yAxis: { type: 'value', name: 'Power (kW)' },
      series: [{ type: 'line', data: data, smooth: true, areaStyle: { opacity: 0.3 }, lineStyle: { color: '#409eff', width: 2 } }]
    })
  } else if (activeChartTab.value === 'temperature') {
    data = Array.from({ length: 24 }, (_, i) => {
      const baseTemp = params.externalTemp
      const hourTemp = baseTemp + (i > 12 ? Math.sin((i - 12) * Math.PI / 12) * 5 : Math.sin(i * Math.PI / 12) * 5)
      return parseFloat(hourTemp.toFixed(1))
    })
    simChart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: hours, name: 'Hour' },
      yAxis: { type: 'value', name: 'Temperature (°C)' },
      series: [{ type: 'line', data: data, smooth: true, areaStyle: { opacity: 0.3 }, lineStyle: { color: '#e6a23c', width: 2 } }]
    })
  } else if (activeChartTab.value === 'cost') {
    data = Array.from({ length: 24 }, () => 5 + Math.random() * 15)
    simChart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: hours, name: 'Hour' },
      yAxis: { type: 'value', name: 'Cost ($/hour)' },
      series: [{ type: 'bar', data: data, itemStyle: { color: '#67c23a', borderRadius: [4, 4, 0, 0] } }]
    })
  }
}

const renderComparisonChart = () => {
  if (!comparisonChartRef.value) return
  if (comparisonChart) comparisonChart.dispose()

  comparisonChart = echarts.init(comparisonChartRef.value)

  const categories = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  let baselineData: number[] = []
  let optimizedData: number[] = []

  if (comparisonMetric.value === 'energy') {
    baselineData = Array.from({ length: 7 }, () => 300 + Math.random() * 100)
    optimizedData = baselineData.map(d => d * (0.7 + Math.random() * 0.1))
  } else if (comparisonMetric.value === 'cost') {
    baselineData = Array.from({ length: 7 }, () => 120 + Math.random() * 40)
    optimizedData = baselineData.map(d => d * (0.65 + Math.random() * 0.15))
  } else {
    baselineData = Array.from({ length: 7 }, () => 50 + Math.random() * 20)
    optimizedData = baselineData.map(d => d * (0.6 + Math.random() * 0.2))
  }

  comparisonChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Baseline', 'Optimized'], top: 0 },
    xAxis: { type: 'category', data: categories },
    yAxis: { type: 'value', name: comparisonMetric.value === 'energy' ? 'Energy (kWh)' : comparisonMetric.value === 'cost' ? 'Cost ($)' : 'CO₂ (kg)' },
    series: [
      { name: 'Baseline', type: 'bar', data: baselineData, itemStyle: { color: '#909399', borderRadius: [4, 4, 0, 0] } },
      { name: 'Optimized', type: 'bar', data: optimizedData, itemStyle: { color: '#67c23a', borderRadius: [4, 4, 0, 0] } }
    ]
  })
}

// ==================== 模拟运行 ====================
const runSimulation = async () => {
  if (isSimulating.value) return

  isSimulating.value = true
  simulationStatus.value = 'running'
  simulationProgress.value = 0

  // Run baseline first if not exists
  if (!baselineResult.value) {
    baselineResult.value = calculateSimulation(presets[0].params, 'Baseline')
  }

  // Simulate progress
  const interval = setInterval(() => {
    if (simulationProgress.value < 100) {
      simulationProgress.value += Math.random() * 15 + 5
      if (simulationProgress.value > 100) simulationProgress.value = 100
    }
  }, 200)

  // Simulate computation delay
  await new Promise(resolve => setTimeout(resolve, 2500))

  clearInterval(interval)
  simulationProgress.value = 100

  const result = calculateSimulation(params, getScenarioName())
  lastResults.value = result
  simulationHistory.value.unshift(result)

  stats.scenariosRun++
  stats.potentialSavings = Math.floor(Math.random() * 30) + 15
  stats.avgSimTime = parseFloat((Math.random() * 3 + 1.5).toFixed(1))

  simulationStatus.value = 'completed'
  isSimulating.value = false

  ElMessage.success(`Simulation "${result.scenarioName}" completed successfully`)

  // Refresh charts
  nextTick(() => {
    renderSimChart()
    renderComparisonChart()
  })
}

const getScenarioName = (): string => {
  if (selectedPreset.value) {
    const preset = presets.find(p => p.id === selectedPreset.value)
    if (preset) return preset.name
  }
  return `Custom Simulation ${new Date().toLocaleTimeString()}`
}

const loadPreset = (preset: Preset) => {
  selectedPreset.value = preset.id
  params.duration = preset.params.duration
  params.hvacSetpoint = preset.params.hvacSetpoint
  params.lightingLevel = preset.params.lightingLevel
  params.equipmentSchedule = preset.params.equipmentSchedule
  params.occupancy = preset.params.occupancy
  params.externalTemp = preset.params.externalTemp
  params.energyPrice = preset.params.energyPrice
  params.mode = preset.params.mode
  ElMessage.info(`Loaded preset: ${preset.name}`)
}

const resetSimulation = () => {
  loadPreset(presets[0])
  simulationStatus.value = 'idle'
  simulationProgress.value = 0
  ElMessage.info('Simulation parameters reset to baseline')
}

const exportResults = () => {
  const exportData = {
    generatedAt: new Date().toISOString(),
    baseline: baselineResult.value,
    lastSimulation: lastResults.value,
    history: simulationHistory.value,
    stats: stats
  }
  const data = JSON.stringify(exportData, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `simulation-results-${new Date().toISOString().slice(0, 19)}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Results exported')
}

const reloadSimulation = (result: SimulationResult) => {
  params.duration = result.params.duration
  params.hvacSetpoint = result.params.hvacSetpoint
  params.lightingLevel = result.params.lightingLevel
  params.equipmentSchedule = result.params.equipmentSchedule
  params.occupancy = result.params.occupancy
  params.externalTemp = result.params.externalTemp
  params.energyPrice = result.params.energyPrice
  params.mode = result.params.mode
  lastResults.value = result
  ElMessage.success(`Loaded simulation: ${result.scenarioName}`)
}

const deleteHistoryItem = (result: SimulationResult) => {
  const index = simulationHistory.value.findIndex(r => r.id === result.id)
  if (index !== -1) {
    simulationHistory.value.splice(index, 1)
    ElMessage.success('Simulation removed from history')
  }
}

const clearHistory = () => {
  simulationHistory.value = []
  ElMessage.info('Simulation history cleared')
}

// ==================== 数据加载 ====================
const loadData = () => {
  // Initialize baseline
  baselineResult.value = calculateSimulation(presets[0].params, 'Baseline')

  nextTick(() => {
    startRenderLoop()
    renderSimChart()
    renderComparisonChart()
  })
}

// ==================== 生命周期 ====================
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
      loadData()
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  if (animationFrameId) cancelAnimationFrame(animationFrameId)
  window.removeEventListener('resize', () => {
    simChart?.resize()
    comparisonChart?.resize()
    compareChart?.resize()
  })
})

watch([viewType, activeChartTab, comparisonMetric], () => {
  nextTick(() => {
    if (viewType.value === 'chart') renderSimChart()
    if (viewType.value === 'comparison') renderComparisonChart()
  })
})

watch(isLoaded, (loaded) => {
  if (loaded) {
    window.addEventListener('resize', () => {
      simChart?.resize()
      comparisonChart?.resize()
      compareChart?.resize()
    })
  }
})
</script>

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

/* ==================== Main Content Styles ==================== */
.scenario-simulation-page {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
  color: #1f2f3d;
}

.page-header p {
  margin: 0;
  color: #5e6e82;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
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

.primary-bg { background-color: #ecf5ff; color: #409eff; }
.success-bg { background-color: #f0f9eb; color: #67c23a; }
.warning-bg { background-color: #fff3e0; color: #e6a23c; }
.info-bg { background-color: #f5f7fa; color: #8c9aab; }

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #8c9aab;
  margin-top: 4px;
}

/* Configuration Card */
.config-card, .visualization-card, .history-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2f3d;
}

.preset-section {
  margin-bottom: 16px;
}

.preset-section label {
  font-size: 13px;
  font-weight: 500;
  color: #5e6e82;
  display: block;
  margin-bottom: 8px;
}

.preset-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.params-form {
  margin-top: 8px;
}

.param-hint {
  margin-left: 12px;
  font-size: 12px;
  color: #8c9aab;
}

.run-section {
  margin-top: 8px;
}

/* Visualization */
.view-controls {
  display: flex;
  gap: 8px;
}

.viewer-container {
  position: relative;
  background-color: #1a1a2e;
  border-radius: 8px;
  overflow: hidden;
}

.viewer-canvas {
  width: 100%;
  height: 400px;
  display: block;
}

.simulation-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.simulation-status {
  background: rgba(0, 0, 0, 0.8);
  padding: 12px 24px;
  border-radius: 8px;
  color: white;
  font-weight: 500;
}

.chart-view, .comparison-view {
  height: 400px;
}

.chart-tabs {
  margin-bottom: 16px;
}

.sim-chart-container, .comparison-chart-container, .compare-chart-container {
  height: 320px;
  width: 100%;
}

.comparison-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

/* Results Summary */
.results-summary {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.summary-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #1f2f3d;
}

.result-card {
  text-align: center;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
}

.result-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
}

.result-unit {
  font-size: 14px;
  font-weight: normal;
  color: #8c9aab;
  margin-left: 4px;
}

.result-label {
  font-size: 12px;
  color: #8c9aab;
  margin-top: 4px;
}

.result-delta {
  font-size: 11px;
  margin-top: 4px;
}

.result-delta.positive { color: #67c23a; }
.result-delta.negative { color: #f56c6c; }

/* History Table */
.history-card {
  overflow: hidden;
}

.no-history {
  padding: 20px 0;
}

.positive { color: #67c23a; }
.negative { color: #f56c6c; }

:deep(.el-table th) {
  background-color: #fafbfc;
  font-weight: 600;
}

:deep(.el-slider__runway) {
  margin: 8px 0;
}
</style>