<template>
  <div class="containment-upgrade-container">
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
            <span class="loading-title">Loading Containment Upgrade</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Hot/Cold Aisle Containment Analysis</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="containment-upgrade-main">
      <!-- Page Header -->
      <div class="page-header">
        <div>
          <h1 class="page-title">Containment Upgrade</h1>
          <p class="page-subtitle">Hot/Cold aisle containment analysis and ROI simulation</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="runSimulation">
            <el-icon><Cpu /></el-icon>
            Run Simulation
          </el-button>
          <el-button @click="exportReport">
            <el-icon><Download /></el-icon>
            Export Report
          </el-button>
          <el-button @click="generateROI">
            <el-icon><TrendCharts /></el-icon>
            Generate ROI Analysis
          </el-button>
        </div>
      </div>

      <!-- Alert Banner -->
      <div v-if="highROIpotential" class="alert-banner success">
        <el-icon><CircleCheck /></el-icon>
        <span>High ROI potential detected! Estimated payback: {{ paybackPeriod }} months. Recommended to proceed.</span>
        <el-button size="small" type="success" @click="startProject">Start Project</el-button>
      </div>

      <!-- Overview Cards -->
      <div class="overview-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="overview-card">
              <div class="card-icon blue">
                <el-icon><OfficeBuilding /></el-icon>
              </div>
              <div class="card-info">
                <span class="card-label">Current Containment</span>
                <span class="card-value">{{ currentContainment }}%</span>
                <el-progress :percentage="currentContainment" :stroke-width="6" color="#3b82f6" :show-text="false" />
                <span class="card-hint">Target: 95%+</span>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="overview-card">
              <div class="card-icon green">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="card-info">
                <span class="card-label">Energy Savings</span>
                <span class="card-value">{{ formatNumber(energySavings) }} kWh/year</span>
                <el-progress :percentage="75" :stroke-width="6" color="#10b981" :show-text="false" />
                <span class="card-hint">{{ energyReduction }}% reduction</span>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="overview-card">
              <div class="card-icon orange">
                <el-icon><Coin /></el-icon>
              </div>
              <div class="card-info">
                <span class="card-label">Cost Savings</span>
                <span class="card-value">${{ formatNumber(costSavings) }}/year</span>
                <el-progress :percentage="75" :stroke-width="6" color="#f59e0b" :show-text="false" />
                <span class="card-hint">ROI: {{ roiPercentage }}%</span>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="overview-card">
              <div class="card-icon purple">
                <el-icon><Clock /></el-icon>
              </div>
              <div class="card-info">
                <span class="card-label">Payback Period</span>
                <span class="card-value">{{ paybackPeriod }} months</span>
                <el-progress :percentage="(paybackPeriod / 24) * 100" :stroke-width="6" color="#8b5cf6" :show-text="false" />
                <span class="card-hint">Project life: 10+ years</span>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- Containment Visualization -->
      <div class="containment-viz-section">
        <el-card class="viz-card" shadow="hover">
          <div class="card-header">
            <div class="card-title">
              <el-icon><Grid /></el-icon>
              <span>Containment Layout Visualization</span>
            </div>
            <el-radio-group v-model="vizType" size="small">
              <el-radio-button label="current">Current</el-radio-button>
              <el-radio-button label="upgraded">Upgraded</el-radio-button>
              <el-radio-button label="comparison">Comparison</el-radio-button>
            </el-radio-group>
          </div>
          <div class="viz-container">
            <div class="data-hall-layout">
              <div class="cold-aisle">
                <div class="aisle-label">Cold Aisle</div>
                <div class="aisle-temp current" :class="{ upgraded: vizType === 'upgraded' }">{{ currentColdTemp }}°C</div>
              </div>
              <div class="rack-row">
                <div v-for="i in 6" :key="i" class="rack">
                  <div class="rack-front">Rack {{ String.fromCharCode(64 + i) }}01</div>
                  <div class="rack-temp" :class="getRackTempClass(getCurrentRackTemp(i))">{{ getCurrentRackTemp(i) }}°C</div>
                </div>
              </div>
              <div class="hot-aisle">
                <div class="aisle-label">Hot Aisle</div>
                <div class="aisle-temp current" :class="{ upgraded: vizType === 'upgraded' }">{{ currentHotTemp }}°C</div>
              </div>
              <div class="rack-row">
                <div v-for="i in 6" :key="i" class="rack">
                  <div class="rack-front">Rack {{ String.fromCharCode(64 + i) }}02</div>
                  <div class="rack-temp" :class="getRackTempClass(getCurrentRackTemp(i + 6))">{{ getCurrentRackTemp(i + 6) }}°C</div>
                </div>
              </div>
              <div class="cold-aisle">
                <div class="aisle-label">Cold Aisle</div>
                <div class="aisle-temp current" :class="{ upgraded: vizType === 'upgraded' }">{{ currentColdTemp }}°C</div>
              </div>
            </div>
          </div>
          <div class="viz-legend">
            <div class="legend-item">
              <span class="legend-color cold"></span>
              <span>Cold Aisle</span>
            </div>
            <div class="legend-item">
              <span class="legend-color hot"></span>
              <span>Hot Aisle</span>
            </div>
            <div class="legend-item">
              <span class="legend-color rack-normal"></span>
              <span>Rack (&lt;26°C)</span>
            </div>
            <div class="legend-item">
              <span class="legend-color rack-warning"></span>
              <span>Rack (26-28°C)</span>
            </div>
            <div class="legend-item">
              <span class="legend-color rack-critical"></span>
              <span>Rack (&gt;28°C)</span>
            </div>
          </div>
        </el-card>
      </div>

      <!-- ROI Analysis -->
      <div class="roi-section">
        <el-row :gutter="20">
          <el-col :span="16">
            <el-card class="roi-card" shadow="hover">
              <div class="card-header">
                <div class="card-title">
                  <el-icon><TrendCharts /></el-icon>
                  <span>Investment ROI Analysis</span>
                </div>
              </div>
              <div class="chart-container">
                <canvas id="roiChart"></canvas>
              </div>
              <div class="roi-stats">
                <div class="roi-stat">
                  <span>Total Investment</span>
                  <strong>${{ formatNumber(totalInvestment) }}</strong>
                </div>
                <div class="roi-stat">
                  <span>Annual Savings</span>
                  <strong>${{ formatNumber(costSavings) }}</strong>
                </div>
                <div class="roi-stat">
                  <span>5-Year Savings</span>
                  <strong>${{ formatNumber(fiveYearSavings) }}</strong>
                </div>
                <div class="roi-stat">
                  <span>10-Year Savings</span>
                  <strong>${{ formatNumber(tenYearSavings) }}</strong>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card class="investment-card" shadow="hover">
              <div class="card-header">
                <div class="card-title">
                  <el-icon><Setting /></el-icon>
                  <span>Investment Breakdown</span>
                </div>
              </div>
              <div class="investment-breakdown">
                <div class="investment-item">
                  <span>Panels & Materials</span>
                  <strong>${{ formatNumber(panelsCost) }}</strong>
                  <el-progress :percentage="(panelsCost / totalInvestment) * 100" :stroke-width="4" color="#3b82f6" />
                </div>
                <div class="investment-item">
                  <span>Installation Labor</span>
                  <strong>${{ formatNumber(laborCost) }}</strong>
                  <el-progress :percentage="(laborCost / totalInvestment) * 100" :stroke-width="4" color="#10b981" />
                </div>
                <div class="investment-item">
                  <span>Engineering & Design</span>
                  <strong>${{ formatNumber(engineeringCost) }}</strong>
                  <el-progress :percentage="(engineeringCost / totalInvestment) * 100" :stroke-width="4" color="#f59e0b" />
                </div>
                <div class="investment-item">
                  <span>Other Costs</span>
                  <strong>${{ formatNumber(otherCost) }}</strong>
                  <el-progress :percentage="(otherCost / totalInvestment) * 100" :stroke-width="4" color="#8b5cf6" />
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Upgrade Scenarios -->
      <div class="scenarios-section">
        <div class="section-header">
          <h3>Upgrade Scenarios</h3>
        </div>
        <el-row :gutter="20">
          <el-col :span="8" v-for="scenario in upgradeScenarios" :key="scenario.id">
            <el-card class="scenario-card" shadow="hover" :class="{ recommended: scenario.recommended }">
              <div class="scenario-header">
                <span class="scenario-name">{{ scenario.name }}</span>
                <el-tag :type="scenario.recommended ? 'success' : 'info'" size="small">
                  {{ scenario.recommended ? 'Recommended' : 'Optional' }}
                </el-tag>
              </div>
              <div class="scenario-content">
                <div class="scenario-metrics">
                  <div class="metric">
                    <span>Containment Efficiency</span>
                    <strong>{{ scenario.efficiency }}%</strong>
                    <el-progress :percentage="scenario.efficiency" :stroke-width="6" :color="scenario.efficiency >= 90 ? '#10b981' : '#f59e0b'" />
                  </div>
                  <div class="metric">
                    <span>Investment</span>
                    <strong>${{ formatNumber(scenario.investment) }}</strong>
                  </div>
                  <div class="metric">
                    <span>Annual Savings</span>
                    <strong>${{ formatNumber(scenario.savings) }}</strong>
                  </div>
                  <div class="metric">
                    <span>Payback</span>
                    <strong>{{ scenario.payback }} months</strong>
                  </div>
                </div>
              </div>
              <div class="scenario-footer">
                <el-button type="primary" size="small" @click="selectScenario(scenario)">Select</el-button>
                <el-button size="small" @click="viewScenarioDetails(scenario)">Details</el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Temperature Improvement -->
      <div class="temperature-section">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card class="temp-card" shadow="hover">
              <div class="card-header">
                <div class="card-title">
                  <el-icon><Setting /></el-icon>
                  <span>Temperature Improvement by Zone</span>
                </div>
              </div>
              <div class="chart-container">
                <canvas id="tempImprovementChart"></canvas>
              </div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card class="temp-card" shadow="hover">
              <div class="card-header">
                <div class="card-title">
                  <el-icon><DataLine /></el-icon>
                  <span>Hotspot Reduction</span>
                </div>
              </div>
              <div class="chart-container">
                <canvas id="hotspotReductionChart"></canvas>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Recommendations -->
      <div class="recommendations-section">
        <div class="section-header">
          <h3>Implementation Recommendations</h3>
        </div>
        <div class="recommendations-grid">
          <div v-for="rec in recommendations" :key="rec.id" class="recommendation-card">
            <div class="rec-check">
              <el-checkbox v-model="rec.selected" />
            </div>
            <div class="rec-content">
              <h4>{{ rec.title }}</h4>
              <p>{{ rec.description }}</p>
              <div class="rec-metrics">
                <span class="rec-impact">Impact: {{ rec.impact }}</span>
                <span class="rec-cost">Cost: ${{ formatNumber(rec.cost) }}</span>
                <span class="rec-savings">Savings: ${{ formatNumber(rec.savings) }}/year</span>
              </div>
            </div>
            <div class="rec-priority" :class="rec.priority">
              {{ rec.priority }}
            </div>
          </div>
        </div>
        <div class="selected-summary">
          <span>Selected items total: <strong>${{ formatNumber(selectedTotalCost) }}</strong></span>
          <span>Expected annual savings: <strong>${{ formatNumber(selectedTotalSavings) }}</strong></span>
          <span>Combined payback: <strong>{{ selectedPayback }} months</strong></span>
          <el-button type="primary" @click="generateImplementationPlan">Generate Implementation Plan</el-button>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="action-buttons">
        <el-button type="primary" size="large" @click="generateDetailedPlan">
          <el-icon><Document /></el-icon>
          Generate Detailed Upgrade Plan
        </el-button>
        <el-button size="large" @click="scheduleInstallation">
          <el-icon><Calendar /></el-icon>
          Schedule Installation
        </el-button>
        <el-button size="large" @click="requestQuote">
          <el-icon><Message /></el-icon>
          Request Quote
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
  Cpu, Download, TrendCharts, Coin, Clock, Grid, Setting,
  DataLine, Document, Calendar, Message, CircleCheck, OfficeBuilding
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading containment upgrade analysis...')

// ==================== Reactive Data ====================
const vizType = ref('current')
const currentContainment = ref(65)
const targetContainment = ref(95)

// Temperature data
const currentColdTemp = ref(22)
const currentHotTemp = ref(32)
const upgradedColdTemp = ref(24)
const upgradedHotTemp = ref(28)

// Cost data
const totalInvestment = ref(75000)
const panelsCost = ref(35000)
const laborCost = ref(25000)
const engineeringCost = ref(10000)
const otherCost = ref(5000)

// Energy and savings
const baselineEnergy = ref(2500000)
const energyReduction = ref(18)
const energySavings = computed(() => baselineEnergy.value * (energyReduction.value / 100))
const electricityRate = ref(0.12)
const costSavings = computed(() => energySavings.value * electricityRate.value)

const paybackPeriod = computed(() => Math.round(totalInvestment.value / (costSavings.value / 12)))
const roiPercentage = computed(() => ((costSavings.value / totalInvestment.value) * 100).toFixed(1))
const fiveYearSavings = computed(() => costSavings.value * 5 - totalInvestment.value)
const tenYearSavings = computed(() => costSavings.value * 10 - totalInvestment.value)
const highROIpotential = computed(() => paybackPeriod.value <= 18)

// Selected recommendations total
const selectedTotalCost = ref(0)
const selectedTotalSavings = ref(0)
const selectedPayback = ref(0)

// Rack temperatures
const getCurrentRackTemp = (index: number) => {
  const baseTemps = [24, 25, 27, 28, 26, 25, 23, 24, 26, 27, 25, 24]
  return baseTemps[index % baseTemps.length]
}

const getUpgradedRackTemp = (index: number) => {
  const baseTemps = [23, 23.5, 24, 24.5, 24, 23.5, 22.5, 23, 24, 24.5, 23.5, 23]
  return baseTemps[index % baseTemps.length]
}

const getRackTempClass = (temp: number) => {
  if (temp < 26) return 'normal'
  if (temp < 28) return 'warning'
  return 'critical'
}

// Upgrade scenarios
const upgradeScenarios = ref([
  { id: 1, name: 'Basic Containment', efficiency: 85, investment: 45000, savings: 45000, payback: 12, recommended: false },
  { id: 2, name: 'Standard Containment', efficiency: 92, investment: 75000, savings: 68000, payback: 13, recommended: true },
  { id: 3, name: 'Premium Containment', efficiency: 98, investment: 120000, savings: 95000, payback: 15, recommended: false }
])

// Recommendations
const recommendations = ref([
  { id: 1, title: 'Install Aisle End Doors', description: 'Seal the ends of hot/cold aisles with acrylic doors', impact: '+15% containment', cost: 15000, savings: 18000, priority: 'high', selected: true },
  { id: 2, title: 'Install Blanking Panels', description: 'Fill empty U spaces in all racks', impact: '+8% containment', cost: 5000, savings: 10000, priority: 'high', selected: true },
  { id: 3, title: 'Seal Cable Cutouts', description: 'Seal all cable openings in raised floor', impact: '+5% containment', cost: 3000, savings: 6000, priority: 'medium', selected: true },
  { id: 4, title: 'Install Brush Seals', description: 'Add brush seals at aisle ends', impact: '+4% containment', cost: 2000, savings: 4000, priority: 'medium', selected: false },
  { id: 5, title: 'Install Overhead Doors', description: 'Overhead aisle containment doors', impact: '+10% containment', cost: 12000, savings: 15000, priority: 'low', selected: false },
  { id: 6, title: 'Install Automatic Doors', description: 'Automatic sliding doors for aisles', impact: '+12% containment', cost: 18000, savings: 22000, priority: 'low', selected: false }
])

// Chart instances
let roiChart: echarts.ECharts | null = null
let tempImprovementChart: echarts.ECharts | null = null
let hotspotReductionChart: echarts.ECharts | null = null

// Helper functions
const formatNumber = (num: number) => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(0) + 'k'
  return num.toString()
}

const runSimulation = () => {
  ElMessage.success('Simulation completed. Results updated.')
}

const exportReport = () => {
  ElMessage.success('Report export started')
}

const generateROI = () => {
  ElMessage.success('ROI analysis generated')
}

const startProject = () => {
  ElMessage.success('Project initiated. Implementation team will contact you.')
}

const selectScenario = (scenario: any) => {
  ElMessage.success(`Selected ${scenario.name} scenario`)
}

const viewScenarioDetails = (scenario: any) => {
  ElMessage.info(`Viewing details for ${scenario.name}`)
}

const generateImplementationPlan = () => {
  ElMessage.success('Implementation plan generated')
}

const generateDetailedPlan = () => {
  ElMessage.success('Detailed upgrade plan generated')
}

const scheduleInstallation = () => {
  ElMessage.info('Installation scheduling interface will open')
}

const requestQuote = () => {
  ElMessage.info('Quote request sent to vendors')
}

// Chart initialization
const initROIChart = () => {
  const canvas = document.getElementById('roiChart') as HTMLCanvasElement
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

  if (roiChart) roiChart.dispose()
  roiChart = echarts.init(canvas, null, { width: width, height: height, devicePixelRatio: pixelRatio })

  const years = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
  const cumulativeSavings = years.map(y => y * costSavings.value)
  const netProfit = cumulativeSavings.map((s, i) => s - totalInvestment.value)

  roiChart.setOption({
    tooltip: { trigger: 'axis', formatter: (params: any) => {
        const year = params[0].axisValue
        const savings = cumulativeSavings[year]
        const profit = netProfit[year]
        return `Year ${year}<br/>Cumulative Savings: $${formatNumber(savings)}<br/>Net Profit: $${formatNumber(profit)}`
      }},
    legend: { data: ['Cumulative Savings', 'Net Profit'], bottom: 0, left: 'center' },
    grid: { top: 40, left: 60, right: 40, bottom: 50, containLabel: true },
    xAxis: { type: 'category', data: years, name: 'Year' },
    yAxis: { type: 'value', name: 'Amount ($)', axisLabel: { formatter: (v: number) => '$' + formatNumber(v) } },
    series: [
      { name: 'Cumulative Savings', type: 'line', data: cumulativeSavings, smooth: true, lineStyle: { color: '#10b981', width: 3 }, areaStyle: { opacity: 0.3, color: '#10b981' }, symbol: 'circle', symbolSize: 8 },
      { name: 'Net Profit', type: 'line', data: netProfit, smooth: true, lineStyle: { color: '#3b82f6', width: 3 }, areaStyle: { opacity: 0.3, color: '#3b82f6' }, symbol: 'diamond', symbolSize: 8 }
    ]
  })
}

const initTempImprovementChart = () => {
  const canvas = document.getElementById('tempImprovementChart') as HTMLCanvasElement
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

  if (tempImprovementChart) tempImprovementChart.dispose()
  tempImprovementChart = echarts.init(canvas, null, { width: width, height: height, devicePixelRatio: pixelRatio })

  const zones = ['Zone A', 'Zone B', 'Zone C', 'Zone D', 'Zone E', 'Zone F']
  const currentTemps = [26.5, 28.2, 27.1, 29.0, 26.8, 27.5]
  const upgradedTemps = [24.2, 25.1, 24.5, 25.8, 24.0, 24.8]

  tempImprovementChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Current Temperature', 'After Containment'], bottom: 0, left: 'center' },
    xAxis: { type: 'category', data: zones },
    yAxis: { type: 'value', name: 'Temperature (°C)' },
    series: [
      { name: 'Current Temperature', type: 'bar', data: currentTemps, itemStyle: { color: '#ef4444', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top', formatter: '{c}°C' } },
      { name: 'After Containment', type: 'bar', data: upgradedTemps, itemStyle: { color: '#10b981', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top', formatter: '{c}°C' } }
    ]
  })
}

const initHotspotReductionChart = () => {
  const canvas = document.getElementById('hotspotReductionChart') as HTMLCanvasElement
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

  if (hotspotReductionChart) hotspotReductionChart.dispose()
  hotspotReductionChart = echarts.init(canvas, null, { width: width, height: height, devicePixelRatio: pixelRatio })

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const currentHotspots = [8, 7, 9, 12, 15, 18, 22, 20, 16, 12, 9, 7]
  const upgradedHotspots = [3, 2, 3, 4, 5, 6, 7, 7, 5, 4, 3, 2]

  hotspotReductionChart.setOption({
    tooltip: { trigger: 'axis', formatter: '{b}: {c} hotspots' },
    legend: { data: ['Current Hotspots', 'After Containment'], bottom: 0, left: 'center' },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'Number of Hotspots' },
    series: [
      { name: 'Current Hotspots', type: 'line', data: currentHotspots, smooth: true, lineStyle: { color: '#ef4444', width: 2 }, areaStyle: { opacity: 0.3, color: '#ef4444' }, symbol: 'circle', symbolSize: 6 },
      { name: 'After Containment', type: 'line', data: upgradedHotspots, smooth: true, lineStyle: { color: '#10b981', width: 2 }, areaStyle: { opacity: 0.3, color: '#10b981' }, symbol: 'circle', symbolSize: 6 }
    ]
  })
}

const refreshAllCharts = () => {
  setTimeout(() => {
    initROIChart()
    initTempImprovementChart()
    initHotspotReductionChart()
  }, 100)
}

// Watch for recommendation selections
watch(() => recommendations.value, () => {
  const selected = recommendations.value.filter(r => r.selected)
  selectedTotalCost.value = selected.reduce((sum, r) => sum + r.cost, 0)
  selectedTotalSavings.value = selected.reduce((sum, r) => sum + r.savings, 0)
  selectedPayback.value = Math.round((selectedTotalCost.value / (selectedTotalSavings.value / 12)) * 10) / 10
}, { deep: true })

// Window resize handler
let resizeTimer: ReturnType<typeof setTimeout> | null = null
const handleResize = () => {
  if (resizeTimer) clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => {
    if (roiChart) roiChart.resize()
    if (tempImprovementChart) tempImprovementChart.resize()
    if (hotspotReductionChart) hotspotReductionChart.resize()
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
  if (roiChart) roiChart.dispose()
  if (tempImprovementChart) tempImprovementChart.dispose()
  if (hotspotReductionChart) hotspotReductionChart.dispose()
})
</script>

<style scoped>
/* ==================== Loading Screen ==================== */
.containment-upgrade-container {
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
.containment-upgrade-main {
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
  font-size: 24px;
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

/* Containment Visualization */
.containment-viz-section {
  margin-bottom: 24px;
}

.viz-card {
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

.viz-container {
  overflow-x: auto;
}

.data-hall-layout {
  min-width: 700px;
}

.cold-aisle, .hot-aisle {
  background: #e2e8f0;
  padding: 12px;
  text-align: center;
  border-radius: 8px;
  margin: 8px 0;
}

.cold-aisle {
  background: #dbeafe;
  border: 1px solid #bfdbfe;
}

.hot-aisle {
  background: #fee2e2;
  border: 1px solid #fecaca;
}

.aisle-label {
  font-weight: 600;
  font-size: 12px;
}

.aisle-temp {
  font-size: 11px;
  margin-top: 4px;
}

.aisle-temp.current {
  color: #ef4444;
}

.aisle-temp.upgraded {
  color: #10b981;
}

.rack-row {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin: 12px 0;
}

.rack {
  width: 100px;
  text-align: center;
  padding: 12px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.rack-front {
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 8px;
}

.rack-temp {
  font-size: 14px;
  font-weight: 700;
}

.rack-temp.normal {
  color: #10b981;
}

.rack-temp.warning {
  color: #f59e0b;
}

.rack-temp.critical {
  color: #ef4444;
}

.viz-legend {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.legend-color {
  width: 16px;
  height: 12px;
  border-radius: 4px;
}

.legend-color.cold { background: #dbeafe; border: 1px solid #bfdbfe; }
.legend-color.hot { background: #fee2e2; border: 1px solid #fecaca; }
.legend-color.rack-normal { background: #10b981; }
.legend-color.rack-warning { background: #f59e0b; }
.legend-color.rack-critical { background: #ef4444; }

/* ROI Section */
.roi-section {
  margin-bottom: 24px;
}

.roi-card, .investment-card {
  border-radius: 20px;
  background: white;
  padding: 20px;
  height: 100%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.chart-container {
  width: 100%;
  min-height: 350px;
  position: relative;
}

.roi-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
}

.roi-stat {
  text-align: center;
}

.roi-stat span {
  display: block;
  font-size: 11px;
  color: #64748b;
  margin-bottom: 4px;
}

.roi-stat strong {
  font-size: 16px;
  color: #1e293b;
}

.investment-breakdown {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.investment-item span {
  display: block;
  font-size: 13px;
  color: #64748b;
  margin-bottom: 4px;
}

.investment-item strong {
  float: right;
  color: #1e293b;
}

/* Scenarios Section */
.scenarios-section {
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

.scenario-card {
  border-radius: 20px;
  background: white;
  padding: 20px;
  height: 100%;
  transition: all 0.2s ease;
  border: 2px solid transparent;
}

.scenario-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.scenario-card.recommended {
  border-color: #10b981;
  background: #ecfdf5;
}

.scenario-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.scenario-name {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.scenario-metrics {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.metric span {
  display: block;
  font-size: 11px;
  color: #64748b;
  margin-bottom: 4px;
}

.metric strong {
  font-size: 14px;
  color: #1e293b;
}

.scenario-footer {
  display: flex;
  gap: 12px;
  justify-content: center;
}

/* Temperature Section */
.temperature-section {
  margin-bottom: 24px;
}

.temp-card {
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

.recommendations-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.recommendation-card {
  background: white;
  border-radius: 16px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
}

.recommendation-card:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.rec-content {
  flex: 1;
}

.rec-content h4 {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 4px 0;
}

.rec-content p {
  font-size: 12px;
  color: #64748b;
  margin: 0;
}

.rec-metrics {
  display: flex;
  gap: 16px;
  margin-top: 8px;
  font-size: 11px;
}

.rec-impact {
  color: #10b981;
}

.rec-cost {
  color: #f59e0b;
}

.rec-savings {
  color: #3b82f6;
}

.rec-priority {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
}

.rec-priority.high {
  background: #fef2f2;
  color: #ef4444;
}

.rec-priority.medium {
  background: #fffbeb;
  color: #f59e0b;
}

.rec-priority.low {
  background: #ecfdf5;
  color: #10b981;
}

.selected-summary {
  background: #f8fafc;
  border-radius: 16px;
  padding: 16px;
  display: flex;
  gap: 24px;
  align-items: center;
  flex-wrap: wrap;
}

.selected-summary span {
  font-size: 13px;
  color: #64748b;
}

.selected-summary strong {
  color: #1e293b;
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
  .containment-upgrade-main { padding: 16px; }
  .roi-stats { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 768px) {
  .page-header { flex-direction: column; align-items: flex-start; gap: 16px; }
  .card-header { flex-direction: column; align-items: flex-start; gap: 12px; }
  .rack-row { flex-wrap: wrap; }
  .roi-stats { grid-template-columns: 1fr; }
  .selected-summary { flex-direction: column; align-items: flex-start; }
  .action-buttons { flex-direction: column; }
  .action-buttons .el-button { width: 100%; }
}
</style>