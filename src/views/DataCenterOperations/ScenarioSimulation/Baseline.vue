<template>
  <div class="baseline-simulation-container">
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
            <span class="loading-title">Loading Baseline Simulation</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Energy & Carbon Baseline Modeling</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="baseline-simulation-main">
      <!-- Page Header -->
      <div class="page-header">
        <div>
          <h1 class="page-title">Baseline Scenario Simulation</h1>
          <p class="page-subtitle">Model and analyze energy consumption and carbon emissions baseline</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="runSimulation">
            <el-icon><Cpu /></el-icon>
            Run Simulation
          </el-button>
          <el-button @click="saveBaseline">
            <el-icon><Document /></el-icon>
            Save Baseline
          </el-button>
          <el-button @click="exportResults">
            <el-icon><Download /></el-icon>
            Export Results
          </el-button>
        </div>
      </div>

      <!-- Simulation Parameters -->
      <div class="simulation-params-section">
        <el-card class="params-card" shadow="hover">
          <div class="card-header">
            <div class="card-title">
              <el-icon><Setting /></el-icon>
              <span>Baseline Parameters</span>
            </div>
          </div>
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="param-group">
                <label>Reference Year</label>
                <el-select v-model="baselineYear" placeholder="Select Year" style="width: 100%">
                  <el-option label="2020" value="2020" />
                  <el-option label="2021" value="2021" />
                  <el-option label="2022" value="2022" />
                  <el-option label="2023" value="2023" />
                  <el-option label="2024" value="2024" />
                </el-select>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="param-group">
                <label>Data Center Type</label>
                <el-select v-model="dataCenterType" placeholder="Select Type" style="width: 100%">
                  <el-option label="Enterprise" value="enterprise" />
                  <el-option label="Colocation" value="colocation" />
                  <el-option label="Cloud/Hyperscale" value="hyperscale" />
                  <el-option label="Edge" value="edge" />
                </el-select>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="param-group">
                <label>Climate Zone</label>
                <el-select v-model="climateZone" placeholder="Select Zone" style="width: 100%">
                  <el-option label="Cool/Marine (Zone 1)" value="zone1" />
                  <el-option label="Temperate (Zone 2)" value="zone2" />
                  <el-option label="Warm (Zone 3)" value="zone3" />
                  <el-option label="Hot/Humid (Zone 4)" value="zone4" />
                  <el-option label="Hot/Arid (Zone 5)" value="zone5" />
                </el-select>
              </div>
            </el-col>
          </el-row>
          <el-row :gutter="20" style="margin-top: 16px">
            <el-col :span="6">
              <div class="param-group">
                <label>IT Load (MW)</label>
                <el-input-number v-model="itLoad" :min="0.5" :max="100" :step="0.5" style="width: 100%" />
              </div>
            </el-col>
            <el-col :span="6">
              <div class="param-group">
                <label>Baseline PUE</label>
                <el-input-number v-model="baselinePUE" :min="1.1" :max="2.5" :step="0.01" :precision="2" style="width: 100%" />
              </div>
            </el-col>
            <el-col :span="6">
              <div class="param-group">
                <label>Grid Carbon Intensity (gCO₂e/kWh)</label>
                <el-input-number v-model="gridIntensity" :min="100" :max="1000" :step="10" style="width: 100%" />
              </div>
            </el-col>
            <el-col :span="6">
              <div class="param-group">
                <label>Renewable Energy (%)</label>
                <el-slider v-model="renewablePercentage" :min="0" :max="100" :step="5" />
              </div>
            </el-col>
          </el-row>
        </el-card>
      </div>

      <!-- Baseline Summary Cards -->
      <div class="summary-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="summary-card">
              <div class="summary-icon blue">
                <el-icon><Cpu /></el-icon>
              </div>
              <div class="summary-info">
                <span class="summary-label">Total Energy (Annual)</span>
                <span class="summary-value">{{ formatNumber(totalEnergy) }} MWh</span>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="summary-card">
              <div class="summary-icon green">
                <el-icon><DataLine /></el-icon>
              </div>
              <div class="summary-info">
                <span class="summary-label">Total Carbon (Annual)</span>
                <span class="summary-value">{{ formatNumber(totalCarbon) }} tCO₂e</span>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="summary-card">
              <div class="summary-icon orange">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="summary-info">
                <span class="summary-label">Carbon Intensity</span>
                <span class="summary-value">{{ formatNumber(carbonIntensity) }} gCO₂e/kWh</span>
              </div>
            </div>
          </el-col>

          <el-col :span="6">
            <div class="summary-card">
              <div class="summary-icon purple">
                <el-icon><Sunny /></el-icon>
              </div>
              <div class="summary-info">
                <span class="summary-label">PUE</span>
                <span class="summary-value">{{ baselinePUE.toFixed(2) }}</span>
              </div>
            </div>
          </el-col>

        </el-row>
      </div>

      <!-- Energy Breakdown -->
      <div class="breakdown-section">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card class="chart-card" shadow="hover">
              <div class="card-header">
                <div class="card-title">
                  <el-icon><PieChart /></el-icon>
                  <span>Energy Consumption Breakdown</span>
                </div>
              </div>
              <div class="chart-container">
                <canvas id="energyBreakdownChart"></canvas>
              </div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card class="chart-card" shadow="hover">
              <div class="card-header">
                <div class="card-title">
                  <el-icon><DataAnalysis /></el-icon>
                  <span>Carbon Emission Breakdown</span>
                </div>
              </div>
              <div class="chart-container">
                <canvas id="carbonBreakdownChart"></canvas>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Monthly Profile -->
      <div class="monthly-section">
        <el-card class="monthly-card" shadow="hover">
          <div class="card-header">
            <div class="card-title">
              <el-icon><TrendCharts /></el-icon>
              <span>Monthly Energy & Carbon Profile</span>
            </div>
            <el-radio-group v-model="monthlyMetric" size="small">
              <el-radio-button label="energy">Energy (MWh)</el-radio-button>
              <el-radio-button label="carbon">Carbon (tCO₂e)</el-radio-button>
            </el-radio-group>
          </div>
          <div class="chart-container">
            <canvas id="monthlyProfileChart"></canvas>
          </div>
        </el-card>
      </div>

      <!-- PUE Analysis -->
      <div class="pue-section">
        <el-row :gutter="20">
          <el-col :span="16">
            <el-card class="pue-card" shadow="hover">
              <div class="card-header">
                <div class="card-title">
                  <el-icon><Monitor /></el-icon>
                  <span>PUE Decomposition Analysis</span>
                </div>
              </div>
              <div class="pue-decomposition">
                <div class="pue-bar">
                  <div class="pue-segment it" :style="{ width: (1 / baselinePUE) * 100 + '%' }">
                    <span>IT Load ({{ ((1 / baselinePUE) * 100).toFixed(1) }}%)</span>
                  </div>
                  <div class="pue-segment cooling" :style="{ width: ((coolingFactor / baselinePUE) * 100) + '%' }">
                    <span>Cooling ({{ ((coolingFactor / baselinePUE) * 100).toFixed(1) }}%)</span>
                  </div>
                  <div class="pue-segment power" :style="{ width: ((powerFactor / baselinePUE) * 100) + '%' }">
                    <span>Power ({{ ((powerFactor / baselinePUE) * 100).toFixed(1) }}%)</span>
                  </div>
                  <div class="pue-segment other" :style="{ width: ((otherFactor / baselinePUE) * 100) + '%' }">
                    <span>Other ({{ ((otherFactor / baselinePUE) * 100).toFixed(1) }}%)</span>
                  </div>
                </div>
                <div class="pue-stats">
                  <div class="pue-stat">
                    <span>Baseline PUE:</span>
                    <strong>{{ baselinePUE.toFixed(2) }}</strong>
                  </div>
                  <div class="pue-stat">
                    <span>Cooling Factor:</span>
                    <strong>{{ coolingFactor.toFixed(2) }}</strong>
                  </div>
                  <div class="pue-stat">
                    <span>Power Factor:</span>
                    <strong>{{ powerFactor.toFixed(2) }}</strong>
                  </div>
                  <div class="pue-stat">
                    <span>Other Factor:</span>
                    <strong>{{ otherFactor.toFixed(2) }}</strong>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card class="pue-comparison-card" shadow="hover">
              <div class="card-header">
                <div class="card-title">
                  <el-icon><Connection /></el-icon>
                  <span>PUE Benchmark</span>
                </div>
              </div>
              <div class="benchmark-container">
                <div class="benchmark-item">
                  <span class="benchmark-label">Our Baseline</span>
                  <span class="benchmark-value">{{ baselinePUE.toFixed(2) }}</span>
                  <div class="benchmark-bar">
                    <div class="bar-fill" :style="{ width: ((baselinePUE - 1) / 1.5) * 100 + '%', background: '#3b82f6' }"></div>
                  </div>
                </div>
                <div class="benchmark-item">
                  <span class="benchmark-label">Industry Average</span>
                  <span class="benchmark-value">1.45</span>
                  <div class="benchmark-bar">
                    <div class="bar-fill" :style="{ width: ((1.45 - 1) / 1.5) * 100 + '%', background: '#909399' }"></div>
                  </div>
                </div>
                <div class="benchmark-item">
                  <span class="benchmark-label">Best Practice</span>
                  <span class="benchmark-value">1.20</span>
                  <div class="benchmark-bar">
                    <div class="bar-fill" :style="{ width: ((1.20 - 1) / 1.5) * 100 + '%', background: '#10b981' }"></div>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Carbon Intensity Factors -->
      <div class="intensity-section">
        <el-card class="intensity-card" shadow="hover">
          <div class="card-header">
            <div class="card-title">
              <el-icon><DataLine /></el-icon>
              <span>Carbon Intensity Factors</span>
            </div>
          </div>
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="factor-item">
                <span class="factor-label">Grid Carbon Intensity</span>
                <span class="factor-value">{{ gridIntensity }} gCO₂e/kWh</span>
                <el-progress :percentage="(gridIntensity / 800) * 100" :stroke-width="6" color="#f59e0b" />
                <span class="factor-note">Market-based (location-specific)</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="factor-item">
                <span class="factor-label">Renewable Energy Factor</span>
                <span class="factor-value">{{ renewablePercentage }}%</span>
                <el-progress :percentage="renewablePercentage" :stroke-width="6" color="#10b981" />
                <span class="factor-note">PPA + RECs</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="factor-item">
                <span class="factor-label">Adjusted Carbon Intensity</span>
                <span class="factor-value">{{ adjustedIntensity }} gCO₂e/kWh</span>
                <el-progress :percentage="(adjustedIntensity / gridIntensity) * 100" :stroke-width="6" color="#3b82f6" />
                <span class="factor-note">After renewable adjustments</span>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </div>

      <!-- Baseline Comparison Table -->
      <div class="comparison-section">
        <div class="section-header">
          <h3>Baseline vs Industry Comparison</h3>
        </div>
        <el-table :data="comparisonData" stripe class="comparison-table">
          <el-table-column prop="metric" label="Metric" width="200" />
          <el-table-column prop="ourBaseline" label="Our Baseline" width="150">
            <template #default="{ row }">
              <span :style="{ color: getComparisonColor(row.ourBaseline, row.industryAvg, row.lowerIsBetter) }">
                {{ row.ourBaseline }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="industryAvg" label="Industry Average" width="150" />
          <el-table-column prop="bestPractice" label="Best Practice" width="150" />
          <el-table-column label="Status" width="120">
            <template #default="{ row }">
              <el-tag :type="getComparisonTag(row.ourBaseline, row.industryAvg, row.lowerIsBetter)" size="small">
                {{ getComparisonStatus(row.ourBaseline, row.industryAvg, row.lowerIsBetter) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="Gap to Best" width="120">
            <template #default="{ row }">
              {{ getGapToBest(row.ourBaseline, row.bestPractice) }}
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Action Buttons -->
      <div class="action-buttons">
        <el-button type="primary" size="large" @click="createScenario">
          <el-icon><MagicStick /></el-icon>
          Create Scenario from Baseline
        </el-button>
        <el-button size="large" @click="generateReport">
          <el-icon><Document /></el-icon>
          Generate Baseline Report
        </el-button>
        <el-button size="large" @click="scheduleReview">
          <el-icon><Calendar /></el-icon>
          Schedule Review Meeting
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
  Cpu, DataLine, TrendCharts, Sunny, PieChart, DataAnalysis, Monitor,
  Connection, Setting, Document, Download, Calendar, MagicStick
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading baseline simulation...')

// ==================== Simulation Parameters ====================
const baselineYear = ref('2023')
const dataCenterType = ref('enterprise')
const climateZone = ref('zone2')
const itLoad = ref(10)
const baselinePUE = ref(1.45)
const gridIntensity = ref(450)
const renewablePercentage = ref(35)
const monthlyMetric = ref('energy')

// Computed factors
const coolingFactor = computed(() => (baselinePUE.value - 1) * 0.55 + 1)
const powerFactor = computed(() => (baselinePUE.value - 1) * 0.25 + 1)
const otherFactor = computed(() => (baselinePUE.value - 1) * 0.2 + 1)

// Computed metrics
const totalEnergy = computed(() => {
  return itLoad.value * 8760 * baselinePUE.value
})

const totalCarbon = computed(() => {
  const gridCarbon = totalEnergy.value * (gridIntensity.value / 1000) * (1 - renewablePercentage.value / 100)
  const renewableCarbon = totalEnergy.value * (gridIntensity.value / 1000) * (renewablePercentage.value / 100) * 0.1
  return Math.round(gridCarbon + renewableCarbon)
})

const carbonIntensity = computed(() => {
  return Math.round((totalCarbon.value / totalEnergy.value) * 1000)
})

const adjustedIntensity = computed(() => {
  return Math.round(gridIntensity.value * (1 - renewablePercentage.value / 100) + gridIntensity.value * (renewablePercentage.value / 100) * 0.1)
})

// Comparison data
const comparisonData = ref([
  { metric: 'PUE', ourBaseline: baselinePUE.value.toFixed(2), industryAvg: '1.45', bestPractice: '1.20', lowerIsBetter: true },
  { metric: 'Carbon Intensity (gCO₂e/kWh)', ourBaseline: carbonIntensity.value.toString(), industryAvg: '380', bestPractice: '200', lowerIsBetter: true },
  { metric: 'Renewable Energy %', ourBaseline: `${renewablePercentage.value}%`, industryAvg: '35%', bestPractice: '75%', lowerIsBetter: false },
  { metric: 'Energy Efficiency (kWh/kW)', ourBaseline: (baselinePUE.value * 8760).toFixed(0), industryAvg: '12700', bestPractice: '10500', lowerIsBetter: true },
  { metric: 'Water Usage Effectiveness', ourBaseline: '1.75', industryAvg: '1.80', bestPractice: '1.40', lowerIsBetter: true }
])

// Helper functions
const formatNumber = (num: number) => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k'
  return num.toString()
}

const getComparisonColor = (value: any, benchmark: any, lowerIsBetter: boolean) => {
  const numValue = parseFloat(value)
  const numBenchmark = parseFloat(benchmark)
  if (isNaN(numValue) || isNaN(numBenchmark)) return '#1e293b'
  if (lowerIsBetter) {
    if (numValue <= numBenchmark) return '#10b981'
    if (numValue <= numBenchmark * 1.1) return '#f59e0b'
    return '#ef4444'
  } else {
    if (numValue >= numBenchmark) return '#10b981'
    if (numValue >= numBenchmark * 0.9) return '#f59e0b'
    return '#ef4444'
  }
}

const getComparisonTag = (value: any, benchmark: any, lowerIsBetter: boolean) => {
  const numValue = parseFloat(value)
  const numBenchmark = parseFloat(benchmark)
  if (isNaN(numValue) || isNaN(numBenchmark)) return 'info'
  if (lowerIsBetter) {
    if (numValue <= numBenchmark) return 'success'
    if (numValue <= numBenchmark * 1.1) return 'warning'
    return 'danger'
  } else {
    if (numValue >= numBenchmark) return 'success'
    if (numValue >= numBenchmark * 0.9) return 'warning'
    return 'danger'
  }
}

const getComparisonStatus = (value: any, benchmark: any, lowerIsBetter: boolean) => {
  const numValue = parseFloat(value)
  const numBenchmark = parseFloat(benchmark)
  if (isNaN(numValue) || isNaN(numBenchmark)) return 'N/A'
  if (lowerIsBetter) {
    if (numValue <= numBenchmark) return 'Better'
    if (numValue <= numBenchmark * 1.1) return 'Average'
    return 'Worse'
  } else {
    if (numValue >= numBenchmark) return 'Better'
    if (numValue >= numBenchmark * 0.9) return 'Average'
    return 'Worse'
  }
}

const getGapToBest = (value: any, best: any) => {
  const numValue = parseFloat(value)
  const numBest = parseFloat(best)
  if (isNaN(numValue) || isNaN(numBest)) return 'N/A'
  const diff = Math.abs(numValue - numBest)
  if (value.includes('%')) return `${diff.toFixed(1)}%`
  if (value.includes('.')) return diff.toFixed(2)
  return Math.round(diff).toString()
}

// Chart instances
let energyBreakdownChart: echarts.ECharts | null = null
let carbonBreakdownChart: echarts.ECharts | null = null
let monthlyProfileChart: echarts.ECharts | null = null

// Chart initialization
const initEnergyBreakdownChart = () => {
  const canvas = document.getElementById('energyBreakdownChart') as HTMLCanvasElement
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

  if (energyBreakdownChart) energyBreakdownChart.dispose()
  energyBreakdownChart = echarts.init(canvas, null, { width: width, height: height, devicePixelRatio: pixelRatio })

  const itEnergy = itLoad.value * 8760
  const coolingEnergy = itEnergy * (baselinePUE.value - 1) * 0.55
  const powerEnergy = itEnergy * (baselinePUE.value - 1) * 0.25
  const otherEnergy = itEnergy * (baselinePUE.value - 1) * 0.2

  energyBreakdownChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c} MWh)' },
    legend: { top: 'bottom' },
    series: [{
      type: 'pie', radius: ['45%', '70%'],
      data: [
        { value: itEnergy, name: 'IT Equipment', itemStyle: { color: '#3b82f6' } },
        { value: coolingEnergy, name: 'Cooling', itemStyle: { color: '#10b981' } },
        { value: powerEnergy, name: 'Power Distribution', itemStyle: { color: '#f59e0b' } },
        { value: otherEnergy, name: 'Other Facilities', itemStyle: { color: '#8b5cf6' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  })
}

const initCarbonBreakdownChart = () => {
  const canvas = document.getElementById('carbonBreakdownChart') as HTMLCanvasElement
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

  if (carbonBreakdownChart) carbonBreakdownChart.dispose()
  carbonBreakdownChart = echarts.init(canvas, null, { width: width, height: height, devicePixelRatio: pixelRatio })

  const scope1 = totalCarbon.value * 0.15
  const scope2 = totalCarbon.value * 0.7
  const scope3 = totalCarbon.value * 0.15

  carbonBreakdownChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c} tCO₂e)' },
    legend: { top: 'bottom' },
    series: [{
      type: 'pie', radius: ['45%', '70%'],
      data: [
        { value: scope1, name: 'Scope 1 (Direct)', itemStyle: { color: '#f59e0b' } },
        { value: scope2, name: 'Scope 2 (Electricity)', itemStyle: { color: '#3b82f6' } },
        { value: scope3, name: 'Scope 3 (Value Chain)', itemStyle: { color: '#10b981' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  })
}

const initMonthlyProfileChart = () => {
  const canvas = document.getElementById('monthlyProfileChart') as HTMLCanvasElement
  if (!canvas) return

  const container = canvas.parentElement
  if (!container) return

  const width = container.clientWidth
  const height = 350

  const pixelRatio = window.devicePixelRatio || 1
  canvas.width = width * pixelRatio
  canvas.height = height * pixelRatio
  canvas.style.width = `${width}px`
  canvas.style.height = `${height}px`

  if (monthlyProfileChart) monthlyProfileChart.dispose()
  monthlyProfileChart = echarts.init(canvas, null, { width: width, height: height, devicePixelRatio: pixelRatio })

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const monthlyEnergy = months.map((_, i) => {
    const variation = 0.85 + Math.sin(i / 6 * Math.PI) * 0.15
    return totalEnergy.value / 12 * variation
  })
  const monthlyCarbon = monthlyEnergy.map(e => e * (carbonIntensity.value / 1000))

  if (monthlyMetric.value === 'energy') {
    monthlyProfileChart.setOption({
      tooltip: { trigger: 'axis', formatter: '{b}: {c} MWh' },
      xAxis: { type: 'category', data: months },
      yAxis: { type: 'value', name: 'Energy (MWh)' },
      series: [{
        type: 'line', data: monthlyEnergy, smooth: true,
        lineStyle: { color: '#3b82f6', width: 3 },
        areaStyle: { opacity: 0.3, color: '#3b82f6' },
        symbol: 'circle', symbolSize: 8,
        label: { show: true, position: 'top', formatter: (p: any) => Math.round(p.value) + ' MWh' }
      }]
    })
  } else {
    monthlyProfileChart.setOption({
      tooltip: { trigger: 'axis', formatter: '{b}: {c} tCO₂e' },
      xAxis: { type: 'category', data: months },
      yAxis: { type: 'value', name: 'Carbon (tCO₂e)' },
      series: [{
        type: 'line', data: monthlyCarbon, smooth: true,
        lineStyle: { color: '#10b981', width: 3 },
        areaStyle: { opacity: 0.3, color: '#10b981' },
        symbol: 'circle', symbolSize: 8,
        label: { show: true, position: 'top', formatter: (p: any) => Math.round(p.value) + ' t' }
      }]
    })
  }
}

// Actions
const runSimulation = () => {
  ElMessage.success('Simulation completed. Baseline updated.')
  refreshAllCharts()
  updateComparisonData()
}

const saveBaseline = () => {
  ElMessage.success('Baseline saved successfully')
}

const exportResults = () => {
  ElMessage.success('Results exported to CSV')
}

const createScenario = () => {
  ElMessage.info('Creating new scenario from baseline')
}

const generateReport = () => {
  ElMessage.success('Baseline report generation started')
}

const scheduleReview = () => {
  ElMessage.info('Review meeting scheduling interface will open')
}

const updateComparisonData = () => {
  comparisonData.value = [
    { metric: 'PUE', ourBaseline: baselinePUE.value.toFixed(2), industryAvg: '1.45', bestPractice: '1.20', lowerIsBetter: true },
    { metric: 'Carbon Intensity (gCO₂e/kWh)', ourBaseline: carbonIntensity.value.toString(), industryAvg: '380', bestPractice: '200', lowerIsBetter: true },
    { metric: 'Renewable Energy %', ourBaseline: `${renewablePercentage.value}%`, industryAvg: '35%', bestPractice: '75%', lowerIsBetter: false },
    { metric: 'Energy Efficiency (kWh/kW)', ourBaseline: (baselinePUE.value * 8760).toFixed(0), industryAvg: '12700', bestPractice: '10500', lowerIsBetter: true },
    { metric: 'Water Usage Effectiveness', ourBaseline: '1.75', industryAvg: '1.80', bestPractice: '1.40', lowerIsBetter: true }
  ]
}

const refreshAllCharts = () => {
  setTimeout(() => {
    initEnergyBreakdownChart()
    initCarbonBreakdownChart()
    initMonthlyProfileChart()
  }, 100)
}

// Watch for parameter changes
watch([baselinePUE, itLoad, gridIntensity, renewablePercentage], () => {
  refreshAllCharts()
  updateComparisonData()
})

watch(monthlyMetric, () => {
  initMonthlyProfileChart()
})

// Window resize handler
let resizeTimer: ReturnType<typeof setTimeout> | null = null
const handleResize = () => {
  if (resizeTimer) clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => {
    if (energyBreakdownChart) energyBreakdownChart.resize()
    if (carbonBreakdownChart) carbonBreakdownChart.resize()
    if (monthlyProfileChart) monthlyProfileChart.resize()
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
  if (energyBreakdownChart) energyBreakdownChart.dispose()
  if (carbonBreakdownChart) carbonBreakdownChart.dispose()
  if (monthlyProfileChart) monthlyProfileChart.dispose()
})
</script>

<style scoped>
/* ==================== Loading Screen ==================== */
.baseline-simulation-container {
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
.baseline-simulation-main {
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

/* Simulation Parameters */
.simulation-params-section {
  margin-bottom: 24px;
}

.params-card {
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

.param-group {
  margin-bottom: 16px;
}

.param-group label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #64748b;
  margin-bottom: 8px;
}

/* Summary Section */
.summary-section {
  margin-bottom: 24px;
}

.summary-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  gap: 16px;
  align-items: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.summary-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.summary-icon {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.summary-icon.blue { background: #eff6ff; color: #3b82f6; }
.summary-icon.green { background: #ecfdf5; color: #10b981; }
.summary-icon.orange { background: #fffbeb; color: #f59e0b; }
.summary-icon.purple { background: #f3e8ff; color: #8b5cf6; }

.summary-info {
  flex: 1;
}

.summary-label {
  display: block;
  font-size: 13px;
  color: #64748b;
  margin-bottom: 4px;
}

.summary-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

/* Charts */
.breakdown-section {
  margin-bottom: 24px;
}

.chart-card {
  border-radius: 20px;
  background: white;
  padding: 20px;
  height: 100%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.chart-container {
  width: 100%;
  min-height: 320px;
  position: relative;
}

/* Monthly Section */
.monthly-section {
  margin-bottom: 24px;
}

.monthly-card {
  border-radius: 20px;
  background: white;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

/* PUE Section */
.pue-section {
  margin-bottom: 24px;
}

.pue-card, .pue-comparison-card {
  border-radius: 20px;
  background: white;
  padding: 20px;
  height: 100%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.pue-decomposition {
  padding: 16px 0;
}

.pue-bar {
  display: flex;
  height: 60px;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 20px;
}

.pue-segment {
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
  font-weight: 600;
}

.pue-segment.it { background: #3b82f6; }
.pue-segment.cooling { background: #10b981; }
.pue-segment.power { background: #f59e0b; }
.pue-segment.other { background: #8b5cf6; }

.pue-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.pue-stat {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  background: #f8fafc;
  border-radius: 8px;
}

.pue-stat strong {
  color: #1e293b;
}

.benchmark-container {
  padding: 8px 0;
}

.benchmark-item {
  margin-bottom: 20px;
}

.benchmark-label {
  display: inline-block;
  font-size: 13px;
  color: #64748b;
  margin-bottom: 6px;
}

.benchmark-value {
  float: right;
  font-weight: 600;
  color: #1e293b;
}

.benchmark-bar {
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
  margin-top: 4px;
}

.bar-fill {
  height: 100%;
  border-radius: 4px;
}

/* Intensity Section */
.intensity-section {
  margin-bottom: 24px;
}

.intensity-card {
  border-radius: 20px;
  background: white;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.factor-item {
  text-align: center;
  padding: 12px;
}

.factor-label {
  display: block;
  font-size: 13px;
  color: #64748b;
  margin-bottom: 8px;
}

.factor-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 12px;
}

.factor-note {
  display: block;
  font-size: 11px;
  color: #94a3b8;
  margin-top: 8px;
}

/* Comparison Section */
.comparison-section {
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

.comparison-table {
  border-radius: 16px;
  overflow: hidden;
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
  .baseline-simulation-main { padding: 16px; }
  .pue-stats { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .page-header { flex-direction: column; align-items: flex-start; gap: 16px; }
  .action-buttons { flex-direction: column; }
  .action-buttons .el-button { width: 100%; }
  .pue-bar { height: 80px; flex-wrap: wrap; }
  .pue-segment { width: 100% !important; height: 20px; }
}
</style>