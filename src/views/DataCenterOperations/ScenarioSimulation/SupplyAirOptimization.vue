<template>
  <div class="supply-air-optimization-container">
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
            <span class="loading-title">Loading Supply Air Optimization</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Supply Air Temperature Optimization</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="supply-air-optimization-main">
      <!-- Page Header -->
      <div class="page-header">
        <div>
          <h1 class="page-title">Supply Air Optimization</h1>
          <p class="page-subtitle">Optimize supply air temperature setpoints for energy efficiency and reliability</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="runOptimization">
            <el-icon><Cpu /></el-icon>
            Run Optimization
          </el-button>
          <el-button @click="exportReport">
            <el-icon><Download /></el-icon>
            Export Report
          </el-button>
          <el-button @click="applySetpoint">
            <el-icon><MagicStick /></el-icon>
            Apply Recommended Setpoint
          </el-button>
        </div>
      </div>

      <!-- Alert Banner -->
      <div v-if="showRecommendation" class="alert-banner success">
        <el-icon><CircleCheck /></el-icon>
        <span>Optimal supply temperature: {{ recommendedSetpoint }}°C. Expected savings: {{ formatNumber(optimalSavings) }} kWh/year.</span>
        <el-button size="small" type="success" @click="applyRecommendedSetpoint">Apply Now</el-button>
      </div>

      <!-- Overview Cards -->
      <div class="overview-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="overview-card">
              <div class="card-icon blue">
                <el-icon><Monitor /></el-icon>
              </div>
              <div class="card-info">
                <span class="card-label">Current Supply Temp</span>
                <span class="card-value">{{ currentSetpoint }}°C</span>
                <el-progress :percentage="((currentSetpoint - 18) / 10) * 100" :stroke-width="6" color="#3b82f6" :show-text="false" />
                <span class="card-hint">ASHRAE Range: 18-27°C</span>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="overview-card">
              <div class="card-icon green">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="card-info">
                <span class="card-label">Current Cooling Energy</span>
                <span class="card-value">{{ formatNumber(currentEnergy) }} kWh/year</span>
                <el-progress :percentage="65" :stroke-width="6" color="#10b981" :show-text="false" />
                <span class="card-hint">Baseline: {{ formatNumber(baselineEnergy) }} kWh</span>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="overview-card">
              <div class="card-icon orange">
                <el-icon><Coin /></el-icon>
              </div>
              <div class="card-info">
                <span class="card-label">Optimization Potential</span>
                <span class="card-value">{{ optimizationPotential }}%</span>
                <el-progress :percentage="optimizationPotential" :stroke-width="6" color="#f59e0b" :show-text="false" />
                <span class="card-hint">Up to {{ formatNumber(potentialSavings) }} kWh savings</span>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="overview-card">
              <div class="card-icon purple">
                <el-icon><Warning /></el-icon>
              </div>
              <div class="card-info">
                <span class="card-label">Safety Margin</span>
                <span class="card-value" :style="{ color: safetyMarginColor }">{{ safetyMargin }}°C</span>
                <el-progress :percentage="(safetyMargin / 10) * 100" :stroke-width="6" :color="safetyMarginColor" :show-text="false" />
                <span class="card-hint">To critical temp: {{ criticalTemp }}°C</span>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- Optimization Chart -->
      <div class="optimization-section">
        <el-card class="optimization-card" shadow="hover">
          <div class="card-header">
            <div class="card-title">
              <el-icon><TrendCharts /></el-icon>
              <span>Supply Temperature vs Energy & Reliability</span>
            </div>
            <div class="chart-controls">
              <el-switch v-model="showASHRAEBounds" active-text="ASHRAE Bounds" />
              <el-switch v-model="showOptimalPoint" active-text="Show Optimal" />
            </div>
          </div>
          <div class="chart-container">
            <canvas id="optimizationCurveChart"></canvas>
          </div>
          <div class="chart-insights">
            <div class="insight-item">
              <el-icon><MagicStick /></el-icon>
              <span>Optimal setpoint: <strong>{{ recommendedSetpoint }}°C</strong></span>
            </div>
            <div class="insight-item">
              <el-icon><DataLine /></el-icon>
              <span>Energy savings: <strong>{{ formatNumber(optimalSavings) }} kWh/year</strong></span>
            </div>
            <div class="insight-item">
              <el-icon><Warning /></el-icon>
              <span>Safety margin maintained: <strong>{{ safetyMarginAtOptimal }}°C</strong> to critical threshold</span>
            </div>
          </div>
        </el-card>
      </div>

      <!-- Trade-off Analysis -->
      <div class="tradeoff-section">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card class="tradeoff-card" shadow="hover">
              <div class="card-header">
                <div class="card-title">
                  <el-icon><DataAnalysis /></el-icon>
                  <span>Energy vs Temperature Trade-off</span>
                </div>
              </div>
              <div class="chart-container">
                <canvas id="energyVsTempChart"></canvas>
              </div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card class="tradeoff-card" shadow="hover">
              <div class="card-header">
                <div class="card-title">
                  <el-icon><PieChart /></el-icon>
                  <span>Savings Breakdown by Component</span>
                </div>
              </div>
              <div class="chart-container">
                <canvas id="savingsBreakdownChart"></canvas>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Scenario Comparison -->
      <div class="scenario-section">
        <el-card class="scenario-card" shadow="hover">
          <div class="card-header">
            <div class="card-title">
              <el-icon><Grid /></el-icon>
              <span>Scenario Comparison</span>
            </div>
            <el-button size="small" @click="compareScenarios">Compare Scenarios</el-button>
          </div>
          <el-table :data="scenarioData" stripe class="scenario-table">
            <el-table-column prop="scenario" label="Scenario" MagicStick />
            <el-table-column prop="setpoint" label="Supply Temp (°C)" />
            <el-table-column prop="energy" label="Cooling Energy (kWh)" MagicStick>
              <template #default="{ row }">
                {{ formatNumber(row.energy) }}
              </template>
            </el-table-column>
            <el-table-column prop="savings" label="Savings vs Baseline" MagicStick>
              <template #default="{ row }">
                <span :style="{ color: row.savings > 0 ? '#10b981' : '#ef4444' }">
                  {{ row.savings > 0 ? '+' : '' }}{{ formatNumber(row.savings) }} kWh
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="savingsPercent" label="Savings %" width="100">
              <template #default="{ row }">
                <el-tag :type="row.savingsPercent > 10 ? 'success' : 'info'" size="small">
                  {{ row.savingsPercent }}%
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="risk" label="Risk Level" width="100">
              <template #default="{ row }">
                <el-tag :type="row.risk === 'Low' ? 'success' : row.risk === 'Medium' ? 'warning' : 'danger'" size="small">
                  {{ row.risk }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="Action" width="100">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="applyScenario(row)">Apply</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>

      <!-- Sensitivity Analysis -->
      <div class="sensitivity-section">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card class="sensitivity-card" shadow="hover">
              <div class="card-header">
                <div class="card-title">
                  <el-icon><DataLine /></el-icon>
                  <span>Load Sensitivity Analysis</span>
                </div>
              </div>
              <div class="chart-container">
                <canvas id="loadSensitivityChart"></canvas>
              </div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card class="sensitivity-card" shadow="hover">
              <div class="card-header">
                <div class="card-title">
                  <el-icon><Monitor /></el-icon>
                  <span>Ambient Temperature Impact</span>
                </div>
              </div>
              <div class="chart-container">
                <canvas id="ambientSensitivityChart"></canvas>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Recommendations -->
      <div class="recommendations-section">
        <div class="section-header">
          <h3>Optimization Recommendations</h3>
        </div>
        <div class="recommendations-grid">
          <div v-for="rec in recommendations" :key="rec.id" class="recommendation-card" :class="rec.priority">
            <div class="rec-icon">
              <el-icon><component :is="rec.icon" /></el-icon>
            </div>
            <div class="rec-content">
              <h4>{{ rec.title }}</h4>
              <p>{{ rec.description }}</p>
              <div class="rec-metrics">
                <span class="rec-impact">Impact: {{ rec.impact }}</span>
                <span class="rec-savings">Savings: {{ rec.savings }}</span>
                <span class="rec-roi">ROI: {{ rec.roi }}</span>
              </div>
            </div>
            <div class="rec-action">
              <el-button type="primary" size="small" @click="applyRecommendation(rec)">Apply</el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="action-buttons">
        <el-button type="primary" size="large" @click="generateOptimizationPlan">
          <el-icon><Document /></el-icon>
          Generate Optimization Plan
        </el-button>
        <el-button size="large" @click="scheduleImplementation">
          <el-icon><Calendar /></el-icon>
          Schedule Implementation
        </el-button>
        <el-button size="large" @click="monitorImpact">
          <el-icon><Monitor /></el-icon>
          Monitor Impact
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Cpu, Download, MagicStick, TrendCharts, Coin, Warning,
  DataAnalysis, PieChart, Grid, DataLine, Document, Calendar, Monitor,
  CircleCheck, Sunny, WindPower
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading supply air optimization...')

// ==================== Simulation Parameters ====================
const currentSetpoint = ref(22)
const baselineEnergy = ref(2500000)
const criticalTemp = ref(27)
const showASHRAEBounds = ref(true)
const showOptimalPoint = ref(true)
const showRecommendation = ref(true)

// IT Load parameters
const itLoad = ref(1000)
const coolingCOP = ref(4.5)
const outsideTemp = ref(25)
const humidity = ref(50)

// Computed values
const currentEnergy = computed(() => {
  // Calculate cooling energy based on setpoint
  const deltaT = 28 - currentSetpoint.value
  const energyPerDelta = baselineEnergy.value / 6
  return baselineEnergy.value - (deltaT - 6) * energyPerDelta
})

const optimizationPotential = computed(() => {
  const minEnergy = calculateEnergyAtSetpoint(24)
  const maxEnergy = calculateEnergyAtSetpoint(18)
  const potential = ((currentEnergy.value - minEnergy) / maxEnergy) * 100
  return Math.min(80, Math.max(0, Math.round(potential)))
})

const potentialSavings = computed(() => {
  return currentEnergy.value - calculateEnergyAtSetpoint(24)
})

const safetyMargin = computed(() => {
  return criticalTemp.value - currentSetpoint.value
})

const safetyMarginColor = computed(() => {
  if (safetyMargin.value >= 5) return '#10b981'
  if (safetyMargin.value >= 3) return '#f59e0b'
  return '#ef4444'
})

const recommendedSetpoint = ref(24)
const optimalSavings = computed(() => {
  return currentEnergy.value - calculateEnergyAtSetpoint(recommendedSetpoint.value)
})

const safetyMarginAtOptimal = computed(() => {
  return criticalTemp.value - recommendedSetpoint.value
})

// Energy calculation function
const calculateEnergyAtSetpoint = (setpoint: number) => {
  const deltaT = 28 - setpoint
  const energyPerDelta = baselineEnergy.value / 6
  return baselineEnergy.value - (deltaT - 6) * energyPerDelta
}

// Helper functions
const formatNumber = (num: number) => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k'
  return num.toString()
}

// Scenario data
const scenarioData = ref([
  { scenario: 'Current', setpoint: 22, energy: 2500000, savings: 0, savingsPercent: 0, risk: 'Low' },
  { scenario: 'Conservative', setpoint: 23, energy: 2380000, savings: 120000, savingsPercent: 4.8, risk: 'Low' },
  { scenario: 'Recommended', setpoint: 24, energy: 2260000, savings: 240000, savingsPercent: 9.6, risk: 'Medium' },
  { scenario: 'Aggressive', setpoint: 25, energy: 2140000, savings: 360000, savingsPercent: 14.4, risk: 'High' },
  { scenario: 'Maximum', setpoint: 26, energy: 2020000, savings: 480000, savingsPercent: 19.2, risk: 'Very High' }
])

// Recommendations
const recommendations = ref([
  { id: 1, title: 'Increase Supply Temp to 24°C', description: 'ASHRAE compliant, optimal balance of efficiency and safety', impact: '-9.6% cooling energy', savings: '240,000 kWh/year', roi: '3 months', priority: 'high', icon: 'Temperature' },
  { id: 2, title: 'Implement ASHRAE Class A2/A3/A4', description: 'Allow higher inlet temperatures based on IT equipment class', impact: '-15% cooling energy', savings: '375,000 kWh/year', roi: '6 months', priority: 'medium', icon: 'Sunny' },
  { id: 3, title: 'Dynamic Setpoint Control', description: 'Adjust based on real-time IT load and ambient conditions', impact: '-12% cooling energy', savings: '300,000 kWh/year', roi: '8 months', priority: 'medium', icon: 'DataLine' }
])

// Chart instances
let optimizationCurveChart: echarts.ECharts | null = null
let energyVsTempChart: echarts.ECharts | null = null
let savingsBreakdownChart: echarts.ECharts | null = null
let loadSensitivityChart: echarts.ECharts | null = null
let ambientSensitivityChart: echarts.ECharts | null = null

// Chart initialization
const initOptimizationCurveChart = () => {
  const canvas = document.getElementById('optimizationCurveChart') as HTMLCanvasElement
  if (!canvas) return

  const container = canvas.parentElement
  if (!container) return

  const width = container.clientWidth
  const height = 380

  const pixelRatio = window.devicePixelRatio || 1
  canvas.width = width * pixelRatio
  canvas.height = height * pixelRatio
  canvas.style.width = `${width}px`
  canvas.style.height = `${height}px`

  if (optimizationCurveChart) optimizationCurveChart.dispose()
  optimizationCurveChart = echarts.init(canvas, null, { width: width, height: height, devicePixelRatio: pixelRatio })

  const temps = [18, 19, 20, 21, 22, 23, 24, 25, 26, 27]
  const energies = temps.map(t => calculateEnergyAtSetpoint(t))
  const maxEnergy = Math.max(...energies)
  const normalizedEnergies = energies.map(e => (e / maxEnergy) * 100)

  const series: any[] = [
    { name: 'Energy Consumption', type: 'line', data: normalizedEnergies, smooth: true, lineStyle: { color: '#3b82f6', width: 3 }, areaStyle: { opacity: 0.2, color: '#3b82f6' }, symbol: 'circle', symbolSize: 8, yAxisIndex: 0 }
  ]

  if (showASHRAEBounds.value) {
    series.push({
      name: 'ASHRAE Range', type: 'line', data: [null, null, null, null, 50, 50, 50, 50, null, null],
      lineStyle: { color: '#10b981', width: 2, type: 'dashed' }, symbol: 'none'
    })
  }

  if (showOptimalPoint.value) {
    series.push({
      name: 'Optimal Point', type: 'scatter', data: [[24, normalizedEnergies[temps.indexOf(24)]]],
      symbolSize: 16, itemStyle: { color: '#ef4444', borderColor: '#fff', borderWidth: 2 }, label: { show: true, formatter: 'Optimal', position: 'top', fontWeight: 'bold' }
    })
  }

  optimizationCurveChart.setOption({
    tooltip: { trigger: 'axis', formatter: (params: any) => {
        const temp = params[0].axisValue
        const energy = energies[temps.indexOf(parseInt(temp))]
        return `Supply Temp: ${temp}°C<br/>Energy: ${formatNumber(energy)} kWh/year<br/>Savings vs 22°C: ${formatNumber(calculateEnergyAtSetpoint(22) - energy)} kWh`
      }},
    legend: { data: ['Energy Consumption', showASHRAEBounds.value ? 'ASHRAE Range' : '', showOptimalPoint.value ? 'Optimal Point' : ''].filter(Boolean), bottom: 0, left: 'center' },
    grid: { top: 40, left: 60, right: 40, bottom: 50, containLabel: true },
    xAxis: { type: 'category', data: temps, name: 'Supply Air Temperature (°C)', nameLocation: 'middle', nameGap: 35 },
    yAxis: { type: 'value', name: 'Relative Energy Consumption (%)', min: 60, max: 100, axisLabel: { formatter: '{value}%' } },
    series: series
  })
}

const initEnergyVsTempChart = () => {
  const canvas = document.getElementById('energyVsTempChart') as HTMLCanvasElement
  if (!canvas) return

  const container = canvas.parentElement
  if (!container) return

  const width = container.clientWidth
  const height = 320

  const pixelRatio = window.devicePixelRatio || 1
  canvas.width = width * pixelRatio
  canvas.height = height * pixelRatio
  canvas.style.width = `${width}px`
  canvas.style.height = `${height}px`

  if (energyVsTempChart) energyVsTempChart.dispose()
  energyVsTempChart = echarts.init(canvas, null, { width: width, height: height, devicePixelRatio: pixelRatio })

  const temps = [18, 19, 20, 21, 22, 23, 24, 25, 26, 27]
  const energies = temps.map(t => calculateEnergyAtSetpoint(t))

  energyVsTempChart.setOption({
    tooltip: { trigger: 'axis', formatter: (params: any) => `Temperature: ${params[0].axisValue}°C\nEnergy: ${formatNumber(params[0].value)} kWh/year` },
    xAxis: { type: 'category', data: temps, name: 'Supply Temperature (°C)' },
    yAxis: { type: 'value', name: 'Cooling Energy (kWh/year)' },
    series: [{
      type: 'bar', data: energies,
      itemStyle: { borderRadius: [8, 8, 0, 0], color: (params: any) => params.dataIndex >= 5 ? '#10b981' : '#3b82f6' },
      label: { show: true, position: 'top', formatter: (p: any) => formatNumber(p.value) }
    }]
  })
}

const initSavingsBreakdownChart = () => {
  const canvas = document.getElementById('savingsBreakdownChart') as HTMLCanvasElement
  if (!canvas) return

  const container = canvas.parentElement
  if (!container) return

  const width = container.clientWidth
  const height = 320

  const pixelRatio = window.devicePixelRatio || 1
  canvas.width = width * pixelRatio
  canvas.height = height * pixelRatio
  canvas.style.width = `${width}px`
  canvas.style.height = `${height}px`

  if (savingsBreakdownChart) savingsBreakdownChart.dispose()
  savingsBreakdownChart = echarts.init(canvas, null, { width: width, height: height, devicePixelRatio: pixelRatio })

  const compressorSavings = optimalSavings.value * 0.55
  const fanSavings = optimalSavings.value * 0.25
  const pumpSavings = optimalSavings.value * 0.2

  savingsBreakdownChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c} kWh)' },
    legend: { top: 'bottom' },
    series: [{
      type: 'pie', radius: ['45%', '70%'],
      data: [
        { value: compressorSavings, name: 'Compressor Savings', itemStyle: { color: '#3b82f6' } },
        { value: fanSavings, name: 'Fan Savings', itemStyle: { color: '#10b981' } },
        { value: pumpSavings, name: 'Pump Savings', itemStyle: { color: '#f59e0b' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  })
}

const initLoadSensitivityChart = () => {
  const canvas = document.getElementById('loadSensitivityChart') as HTMLCanvasElement
  if (!canvas) return

  const container = canvas.parentElement
  if (!container) return

  const width = container.clientWidth
  const height = 320

  const pixelRatio = window.devicePixelRatio || 1
  canvas.width = width * pixelRatio
  canvas.height = height * pixelRatio
  canvas.style.width = `${width}px`
  canvas.style.height = `${height}px`

  if (loadSensitivityChart) loadSensitivityChart.dispose()
  loadSensitivityChart = echarts.init(canvas, null, { width: width, height: height, devicePixelRatio: pixelRatio })

  const loads = [500, 750, 1000, 1250, 1500, 1750, 2000]
  const savingsAt24 = loads.map(l => {
    const baseEnergy = l * 8760 * 1.45
    const energyAt22 = baseEnergy * 0.45
    const energyAt24 = baseEnergy * 0.4
    return (energyAt22 - energyAt24) / 1000
  })

  loadSensitivityChart.setOption({
    tooltip: { trigger: 'axis', formatter: '{b} kW IT Load\nSavings: {c}k kWh/year' },
    xAxis: { type: 'category', data: loads, name: 'IT Load (kW)' },
    yAxis: { type: 'value', name: 'Annual Savings (k kWh)' },
    series: [{
      type: 'line', data: savingsAt24, smooth: true,
      lineStyle: { color: '#3b82f6', width: 3 },
      areaStyle: { opacity: 0.3, color: '#3b82f6' },
      symbol: 'circle', symbolSize: 8,
      label: { show: true, position: 'top', formatter: '{c}k kWh' }
    }]
  })
}

const initAmbientSensitivityChart = () => {
  const canvas = document.getElementById('ambientSensitivityChart') as HTMLCanvasElement
  if (!canvas) return

  const container = canvas.parentElement
  if (!container) return

  const width = container.clientWidth
  const height = 320

  const pixelRatio = window.devicePixelRatio || 1
  canvas.width = width * pixelRatio
  canvas.height = height * pixelRatio
  canvas.style.width = `${width}px`
  canvas.style.height = `${height}px`

  if (ambientSensitivityChart) ambientSensitivityChart.dispose()
  ambientSensitivityChart = echarts.init(canvas, null, { width: width, height: height, devicePixelRatio: pixelRatio })

  const temps = [15, 18, 21, 24, 27, 30, 33]
  const savingsAt24 = temps.map(t => {
    const baseFactor = 1 + (t - 25) * 0.05
    const energyAt22 = baselineEnergy.value * baseFactor
    const energyAt24 = baselineEnergy.value * baseFactor * 0.9
    return (energyAt22 - energyAt24) / 1000
  })

  ambientSensitivityChart.setOption({
    tooltip: { trigger: 'axis', formatter: '{b}°C Ambient\nSavings: {c}k kWh/year' },
    xAxis: { type: 'category', data: temps, name: 'Ambient Temperature (°C)' },
    yAxis: { type: 'value', name: 'Annual Savings (k kWh)' },
    series: [{
      type: 'line', data: savingsAt24, smooth: true,
      lineStyle: { color: '#f59e0b', width: 3 },
      areaStyle: { opacity: 0.3, color: '#f59e0b' },
      symbol: 'circle', symbolSize: 8,
      label: { show: true, position: 'top', formatter: '{c}k kWh' }
    }]
  })
}

const refreshAllCharts = () => {
  setTimeout(() => {
    initOptimizationCurveChart()
    initEnergyVsTempChart()
    initSavingsBreakdownChart()
    initLoadSensitivityChart()
    initAmbientSensitivityChart()
  }, 100)
}

// Actions
const runOptimization = () => {
  ElMessage.success('Optimization completed. Optimal setpoint: 24°C')
  refreshAllCharts()
}

const exportReport = () => {
  ElMessage.success('Report export started')
}

const applySetpoint = () => {
  ElMessage.success(`Setpoint changed to ${recommendedSetpoint.value}°C`)
  currentSetpoint.value = recommendedSetpoint.value
  refreshAllCharts()
}

const applyRecommendedSetpoint = () => {
  applySetpoint()
}

const applyScenario = (scenario: any) => {
  ElMessage.success(`Applied scenario: ${scenario.scenario} (${scenario.setpoint}°C)`)
  currentSetpoint.value = scenario.setpoint
  refreshAllCharts()
}

const compareScenarios = () => {
  ElMessage.info('Scenario comparison tool will open')
}

const applyRecommendation = (rec: any) => {
  if (rec.title.includes('24°C')) {
    applyRecommendedSetpoint()
  } else {
    ElMessage.success(`Applied: ${rec.title}`)
  }
}

const generateOptimizationPlan = () => {
  ElMessage.success('Optimization plan generated')
}

const scheduleImplementation = () => {
  ElMessage.info('Implementation scheduling interface will open')
}

const monitorImpact = () => {
  ElMessage.info('Impact monitoring dashboard will open')
}

// Watch for toggle changes
watch([showASHRAEBounds, showOptimalPoint], () => {
  initOptimizationCurveChart()
})

// Window resize handler
let resizeTimer: ReturnType<typeof setTimeout> | null = null
const handleResize = () => {
  if (resizeTimer) clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => {
    if (optimizationCurveChart) optimizationCurveChart.resize()
    if (energyVsTempChart) energyVsTempChart.resize()
    if (savingsBreakdownChart) savingsBreakdownChart.resize()
    if (loadSensitivityChart) loadSensitivityChart.resize()
    if (ambientSensitivityChart) ambientSensitivityChart.resize()
  }, 200)
}

// Loading simulation
const startLoading = () => {
  const interval = setInterval(() => {
    if (loadingProgress.value < 90) loadingProgress.value += Math.random() * 10
  }, 200)
  return interval
}

onMounted(() => {
  const interval = startLoading()
  setTimeout(() => {
    clearInterval(interval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(() => {
      isLoaded.value = true
      nextTick(() => {
        setTimeout(() => {
          refreshAllCharts()
          window.addEventListener('resize', handleResize)
        }, 200)
      })
    }, 400)
  }, 2800)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (resizeTimer) clearTimeout(resizeTimer)
  if (optimizationCurveChart) optimizationCurveChart.dispose()
  if (energyVsTempChart) energyVsTempChart.dispose()
  if (savingsBreakdownChart) savingsBreakdownChart.dispose()
  if (loadSensitivityChart) loadSensitivityChart.dispose()
  if (ambientSensitivityChart) ambientSensitivityChart.dispose()
})
</script>

<style scoped>
/* ==================== Loading Screen ==================== */
.supply-air-optimization-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #eef2f6 100%);
}

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
  font-size: 24px;
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
  width: 320px;
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
.supply-air-optimization-main {
  padding: 24px 32px;
  min-height: 100vh;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 4px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Alert Banner */
.alert-banner {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  border-radius: 12px;
  margin-bottom: 20px;
}

.alert-banner.success {
  background: #ecfdf5;
  border-left: 4px solid #10b981;
  color: #059669;
}

.alert-banner .el-icon {
  font-size: 20px;
}

.alert-banner span {
  flex: 1;
  font-weight: 500;
}

/* Overview Cards */
.overview-section {
  margin-bottom: 24px;
}

.overview-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  gap: 16px;
  align-items: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.overview-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.card-icon {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.card-icon.blue { background: #eff6ff; color: #3b82f6; }
.card-icon.green { background: #ecfdf5; color: #10b981; }
.card-icon.orange { background: #fffbeb; color: #f59e0b; }
.card-icon.purple { background: #f3e8ff; color: #8b5cf6; }

.card-info {
  flex: 1;
}

.card-label {
  display: block;
  font-size: 13px;
  color: #64748b;
  margin-bottom: 4px;
}

.card-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.card-hint {
  display: block;
  font-size: 11px;
  color: #94a3b8;
  margin-top: 4px;
}

/* Optimization Section */
.optimization-section {
  margin-bottom: 24px;
}

.optimization-card {
  border-radius: 20px;
  background: white;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e2e8f0;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.card-title .el-icon {
  font-size: 18px;
  color: #3b82f6;
}

.chart-controls {
  display: flex;
  gap: 16px;
  align-items: center;
}

.chart-container {
  width: 100%;
  min-height: 380px;
  position: relative;
}

.chart-insights {
  display: flex;
  justify-content: space-around;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
}

.insight-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #64748b;
}

.insight-item strong {
  color: #1e293b;
}

/* Tradeoff Section */
.tradeoff-section {
  margin-bottom: 24px;
}

.tradeoff-card {
  border-radius: 20px;
  background: white;
  padding: 20px;
  height: 100%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

/* Scenario Section */
.scenario-section {
  margin-bottom: 24px;
}

.scenario-card {
  border-radius: 20px;
  background: white;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.scenario-table {
  border-radius: 16px;
  overflow: hidden;
}

/* Sensitivity Section */
.sensitivity-section {
  margin-bottom: 24px;
}

.sensitivity-card {
  border-radius: 20px;
  background: white;
  padding: 20px;
  height: 100%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

/* Recommendations Section */
.recommendations-section {
  margin-bottom: 24px;
}

.section-header {
  margin-bottom: 16px;
}

.section-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.recommendations-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.recommendation-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  gap: 20px;
  align-items: flex-start;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border-left: 4px solid;
  transition: all 0.2s ease;
}

.recommendation-card:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.recommendation-card.high {
  border-left-color: #ef4444;
}

.recommendation-card.medium {
  border-left-color: #f59e0b;
}

.rec-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #3b82f6;
}

.rec-content {
  flex: 1;
}

.rec-content h4 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 4px 0;
}

.rec-content p {
  font-size: 13px;
  color: #64748b;
  margin: 0 0 8px 0;
}

.rec-metrics {
  display: flex;
  gap: 16px;
  font-size: 12px;
}

.rec-impact {
  color: #10b981;
}

.rec-savings {
  color: #f59e0b;
}

.rec-roi {
  color: #3b82f6;
}

.rec-action {
  flex-shrink: 0;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 24px;
}

.action-buttons .el-button {
  border-radius: 12px;
  padding: 10px 20px;
}

/* Responsive */
@media (max-width: 1200px) {
  .supply-air-optimization-main { padding: 16px; }
}

@media (max-width: 768px) {
  .page-header { flex-direction: column; align-items: flex-start; gap: 16px; }
  .card-header { flex-direction: column; align-items: flex-start; gap: 12px; }
  .chart-insights { flex-direction: column; gap: 12px; }
  .recommendation-card { flex-direction: column; }
  .rec-action { align-self: flex-end; }
  .action-buttons { flex-direction: column; }
  .action-buttons .el-button { width: 100%; }
}
</style>