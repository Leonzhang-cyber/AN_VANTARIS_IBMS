<template>
  <div class="roi-simulation-container">
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
            <span class="loading-title">Loading ROI Simulation</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Investment Return Analysis</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="roi-simulation-main">
      <!-- Page Header -->
      <div class="page-header">
        <div>
          <h1 class="page-title">ROI Simulation</h1>
          <p class="page-subtitle">Calculate and compare investment returns for energy efficiency projects</p>
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
          <el-button @click="compareProjects">
            <el-icon><TrendCharts /></el-icon>
            Compare Projects
          </el-button>
        </div>
      </div>

      <!-- Project Selection -->
      <div class="project-section">
        <el-card class="project-card" shadow="hover">
          <div class="card-header">
            <div class="card-title">
              <el-icon><Setting /></el-icon>
              <span>Project Configuration</span>
            </div>
          </div>
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="param-group">
                <label>Project Type</label>
                <el-select v-model="projectType" placeholder="Select Project Type" style="width: 100%" @change="updateProjectParameters">
                  <el-option label="Cooling Optimization" value="cooling" />
                  <el-option label="Lighting Upgrade" value="lighting" />
                  <el-option label="UPS Upgrade" value="ups" />
                  <el-option label="Containment Installation" value="containment" />
                  <el-option label="Free Cooling Implementation" value="freeCooling" />
                  <el-option label="Custom Project" value="custom" />
                </el-select>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="param-group">
                <label>Initial Investment ($)</label>
                <el-input-number v-model="investment" :min="1000" :max="1000000" :step="10000" style="width: 100%" />
              </div>
            </el-col>
            <el-col :span="8">
              <div class="param-group">
                <label>Annual Savings ($)</label>
                <el-input-number v-model="annualSavings" :min="500" :max="500000" :step="5000" style="width: 100%" />
              </div>
            </el-col>
          </el-row>
          <el-row :gutter="20" style="margin-top: 16px">
            <el-col :span="8">
              <div class="param-group">
                <label>Project Lifetime (years)</label>
                <el-slider v-model="lifetime" :min="1" :max="20" :step="1" show-stops />
              </div>
            </el-col>
            <el-col :span="8">
              <div class="param-group">
                <label>Discount Rate (%)</label>
                <el-slider v-model="discountRate" :min="0" :max="15" :step="0.5" show-stops />
              </div>
            </el-col>
            <el-col :span="8">
              <div class="param-group">
                <label>Electricity Rate ($/kWh)</label>
                <el-input-number v-model="electricityRate" :min="0.05" :max="0.5" :step="0.01" :precision="2" style="width: 100%" />
              </div>
            </el-col>
          </el-row>
        </el-card>
      </div>

      <!-- Key Metrics Cards -->
      <div class="metrics-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="metric-card">
              <div class="metric-icon blue">
                <el-icon><Coin /></el-icon>
              </div>
              <div class="metric-info">
                <span class="metric-label">Net Present Value (NPV)</span>
                <span class="metric-value" :style="{ color: npv >= 0 ? '#10b981' : '#ef4444' }">
                  ${{ formatNumber(npv) }}
                </span>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="metric-card">
              <div class="metric-icon green">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="metric-info">
                <span class="metric-label">Internal Rate of Return (IRR)</span>
                <span class="metric-value">{{ irr }}%</span>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="metric-card">
              <div class="metric-icon orange">
                <el-icon><Clock /></el-icon>
              </div>
              <div class="metric-info">
                <span class="metric-label">Payback Period</span>
                <span class="metric-value">{{ paybackPeriod }} months</span>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="metric-card">
              <div class="metric-icon purple">
                <el-icon><DataLine /></el-icon>
              </div>
              <div class="metric-info">
                <span class="metric-label">Benefit-Cost Ratio</span>
                <span class="metric-value">{{ benefitCostRatio.toFixed(2) }}</span>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- ROI Chart -->
      <div class="chart-section">
        <el-card class="chart-card" shadow="hover">
          <div class="card-header">
            <div class="card-title">
              <el-icon><TrendCharts /></el-icon>
              <span>Financial Analysis</span>
            </div>
            <el-radio-group v-model="chartType" size="small">
              <el-radio-button label="cumulative">Cumulative Cash Flow</el-radio-button>
              <el-radio-button label="annual">Annual Cash Flow</el-radio-button>
            </el-radio-group>
          </div>
          <div class="chart-container">
            <canvas id="roiChart"></canvas>
          </div>
        </el-card>
      </div>

      <!-- Annual Breakdown Table -->
      <div class="table-section">
        <el-card class="table-card" shadow="hover">
          <div class="card-header">
            <div class="card-title">
              <el-icon><List /></el-icon>
              <span>Annual Cash Flow Breakdown</span>
            </div>
          </div>
          <el-table :data="annualData" stripe class="cashflow-table">
            <el-table-column prop="year" label="Year" width="80" />
            <el-table-column prop="investment" label="Investment ($)" width="150">
              <template #default="{ row }">
                ${{ formatNumber(row.investment) }}
              </template>
            </el-table-column>
            <el-table-column prop="savings" label="Annual Savings ($)" width="150">
              <template #default="{ row }">
                ${{ formatNumber(row.savings) }}
              </template>
            </el-table-column>
            <el-table-column prop="netCashFlow" label="Net Cash Flow ($)" width="150">
              <template #default="{ row }">
                <span :style="{ color: row.netCashFlow >= 0 ? '#10b981' : '#ef4444' }">
                  ${{ formatNumber(row.netCashFlow) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="cumulativeCashFlow" label="Cumulative Cash Flow ($)" width="180">
              <template #default="{ row }">
                <span :style="{ color: row.cumulativeCashFlow >= 0 ? '#10b981' : '#ef4444' }">
                  ${{ formatNumber(row.cumulativeCashFlow) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="discountedCashFlow" label="Discounted Cash Flow ($)" width="180">
              <template #default="{ row }">
                ${{ formatNumber(row.discountedCashFlow) }}
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
                  <el-icon><DataAnalysis /></el-icon>
                  <span>Investment Sensitivity</span>
                </div>
              </div>
              <div class="chart-container">
                <canvas id="investmentSensitivityChart"></canvas>
              </div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card class="sensitivity-card" shadow="hover">
              <div class="card-header">
                <div class="card-title">
                  <el-icon><DataLine /></el-icon>
                  <span>Savings Sensitivity</span>
                </div>
              </div>
              <div class="chart-container">
                <canvas id="savingsSensitivityChart"></canvas>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Project Comparison -->
      <div class="comparison-section">
        <div class="section-header">
          <h3>Project Comparison</h3>
          <el-button type="primary" link @click="addComparisonProject">+ Add Project</el-button>
        </div>
        <el-table :data="comparisonProjects" stripe class="comparison-table">
          <el-table-column prop="name" label="Project Name" width="200" />
          <el-table-column prop="investment" label="Investment ($)" width="150">
            <template #default="{ row }">
              ${{ formatNumber(row.investment) }}
            </template>
          </el-table-column>
          <el-table-column prop="annualSavings" label="Annual Savings ($)" width="150">
            <template #default="{ row }">
              ${{ formatNumber(row.annualSavings) }}
            </template>
          </el-table-column>
          <el-table-column prop="npv" label="NPV ($)" width="150">
            <template #default="{ row }">
              <span :style="{ color: row.npv >= 0 ? '#10b981' : '#ef4444' }">
                ${{ formatNumber(row.npv) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="irr" label="IRR (%)" width="100">
            <template #default="{ row }">
              {{ row.irr }}%
            </template>
          </el-table-column>
          <el-table-column prop="payback" label="Payback (months)" width="120" />
          <el-table-column prop="bcr" label="Benefit-Cost Ratio" width="140" />
          <el-table-column label="Action" width="100">
            <template #default="{ row }">
              <el-button type="danger" link size="small" @click="removeComparisonProject(row)">Remove</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Recommendations -->
      <div class="recommendations-section">
        <el-card class="recommendations-card" shadow="hover">
          <div class="card-header">
            <div class="card-title">
              <el-icon><Setting /></el-icon>
              <span>Investment Recommendations</span>
            </div>
          </div>
          <div class="recommendations-content">
            <div class="recommendation-item" v-for="rec in investmentRecommendations" :key="rec.id">
              <div class="rec-status" :class="rec.status"></div>
              <div class="rec-content">
                <h4>{{ rec.title }}</h4>
                <p>{{ rec.description }}</p>
                <div class="rec-metrics">
                  <span>Expected ROI: {{ rec.roi }}</span>
                  <span>Payback: {{ rec.payback }}</span>
                </div>
              </div>
              <div class="rec-action">
                <el-button type="primary" size="small" @click="applyRecommendation(rec)">Apply</el-button>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- Action Buttons -->
      <div class="action-buttons">
        <el-button type="primary" size="large" @click="generateReport">
          <el-icon><Document /></el-icon>
          Generate Full Report
        </el-button>
        <el-button size="large" @click="saveScenario">
          <el-icon><Star /></el-icon>
          Save Scenario
        </el-button>
        <el-button size="large" @click="exportToExcel">
          <el-icon><Download /></el-icon>
          Export to Excel
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
  Cpu, Download, TrendCharts, Coin, Clock, DataLine, Setting,
  List, DataAnalysis, Document, Star, WarningFilled
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading ROI simulation...')

// ==================== Project Parameters ====================
const projectType = ref('cooling')
const investment = ref(75000)
const annualSavings = ref(45000)
const lifetime = ref(10)
const discountRate = ref(8)
const electricityRate = ref(0.12)
const chartType = ref('cumulative')

// Project presets
const projectPresets: Record<string, { investment: number; savings: number; lifetime: number }> = {
  cooling: { investment: 75000, savings: 45000, lifetime: 10 },
  lighting: { investment: 35000, savings: 25000, lifetime: 8 },
  ups: { investment: 150000, savings: 60000, lifetime: 12 },
  containment: { investment: 80000, savings: 50000, lifetime: 10 },
  freeCooling: { investment: 120000, savings: 70000, lifetime: 12 },
  custom: { investment: 75000, savings: 45000, lifetime: 10 }
}

// Computed financial metrics
const npv = computed(() => {
  let npvValue = -investment.value
  for (let year = 1; year <= lifetime.value; year++) {
    npvValue += annualSavings.value / Math.pow(1 + discountRate.value / 100, year)
  }
  return Math.round(npvValue)
})

const irr = computed(() => {
  let guess = 0.1
  let npvValue = -investment.value
  for (let year = 1; year <= lifetime.value; year++) {
    npvValue += annualSavings.value / Math.pow(1 + guess, year)
  }

  if (npvValue > 0) {
    guess = 0.2
    npvValue = -investment.value
    for (let year = 1; year <= lifetime.value; year++) {
      npvValue += annualSavings.value / Math.pow(1 + guess, year)
    }
  }

  return Math.round(guess * 100)
})

const paybackPeriod = computed(() => {
  return Math.round((investment.value / annualSavings.value) * 12)
})

const benefitCostRatio = computed(() => {
  let pvBenefits = 0
  for (let year = 1; year <= lifetime.value; year++) {
    pvBenefits += annualSavings.value / Math.pow(1 + discountRate.value / 100, year)
  }
  return pvBenefits / investment.value
})

// Annual data for table
const annualData = computed(() => {
  const data = []
  let cumulative = -investment.value

  for (let year = 0; year <= lifetime.value; year++) {
    if (year === 0) {
      data.push({
        year: 0,
        investment: investment.value,
        savings: 0,
        netCashFlow: -investment.value,
        cumulativeCashFlow: -investment.value,
        discountedCashFlow: -investment.value
      })
    } else {
      const netCashFlow = annualSavings.value
      cumulative += netCashFlow
      const discountedCashFlow = netCashFlow / Math.pow(1 + discountRate.value / 100, year)
      data.push({
        year: year,
        investment: 0,
        savings: annualSavings.value,
        netCashFlow: netCashFlow,
        cumulativeCashFlow: cumulative,
        discountedCashFlow: Math.round(discountedCashFlow)
      })
    }
  }
  return data
})

// Comparison projects
const comparisonProjects = ref([
  { id: 1, name: 'Cooling Optimization', investment: 75000, annualSavings: 45000, npv: 0, irr: 0, payback: 0, bcr: 0 },
  { id: 2, name: 'LED Lighting Upgrade', investment: 35000, annualSavings: 25000, npv: 0, irr: 0, payback: 0, bcr: 0 }
])

// Investment recommendations
const investmentRecommendations = ref([
  { id: 1, title: 'High ROI Project Detected', description: 'This project shows strong financial returns', status: 'positive', roi: '>25%', payback: '<18 months' },
  { id: 2, title: 'Consider Incentive Programs', description: 'Check for utility rebates and tax incentives', status: 'neutral', roi: '15-25%', payback: '18-36 months' },
  { id: 3, title: 'Optimize Project Scope', description: 'Additional measures could improve returns', status: 'neutral', roi: 'Variable', payback: 'Variable' }
])

// Helper functions
const formatNumber = (num: number) => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k'
  return num.toString()
}

const updateProjectParameters = () => {
  const preset = projectPresets[projectType.value]
  if (preset && projectType.value !== 'custom') {
    investment.value = preset.investment
    annualSavings.value = preset.savings
    lifetime.value = preset.lifetime
  }
}

const runSimulation = () => {
  ElMessage.success('ROI simulation completed')
  refreshAllCharts()
  updateComparisonProjects()
}

const exportReport = () => {
  ElMessage.success('Report export started')
}

const compareProjects = () => {
  ElMessage.info('Project comparison tool will open')
}

const addComparisonProject = () => {
  ElMessage.info('Add project interface will open')
}

const removeComparisonProject = (project: any) => {
  const index = comparisonProjects.value.findIndex(p => p.id === project.id)
  if (index !== -1) {
    comparisonProjects.value.splice(index, 1)
    ElMessage.success('Project removed from comparison')
  }
}

const applyRecommendation = (rec: any) => {
  ElMessage.success(`Applied recommendation: ${rec.title}`)
}

const generateReport = () => {
  ElMessage.success('Full report generation started')
}

const saveScenario = () => {
  ElMessage.success('Scenario saved')
}

const exportToExcel = () => {
  ElMessage.success('Excel export started')
}

const updateComparisonProjects = () => {
  comparisonProjects.value.forEach(project => {
    let npvValue = -project.investment
    for (let year = 1; year <= lifetime.value; year++) {
      npvValue += project.annualSavings / Math.pow(1 + discountRate.value / 100, year)
    }
    project.npv = Math.round(npvValue)
    project.payback = Math.round((project.investment / project.annualSavings) * 12)

    let guess = 0.1
    let npvCalc = -project.investment
    for (let year = 1; year <= lifetime.value; year++) {
      npvCalc += project.annualSavings / Math.pow(1 + guess, year)
    }
    project.irr = Math.round(guess * 100)

    let pvBenefits = 0
    for (let year = 1; year <= lifetime.value; year++) {
      pvBenefits += project.annualSavings / Math.pow(1 + discountRate.value / 100, year)
    }
    project.bcr = pvBenefits / project.investment
  })
}

// Chart instances
let roiChart: echarts.ECharts | null = null
let investmentSensitivityChart: echarts.ECharts | null = null
let savingsSensitivityChart: echarts.ECharts | null = null

// Chart initialization
const initROIChart = () => {
  const canvas = document.getElementById('roiChart') as HTMLCanvasElement
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

  if (roiChart) roiChart.dispose()
  roiChart = echarts.init(canvas, null, { width: width, height: height, devicePixelRatio: pixelRatio })

  const years = annualData.value.map(d => d.year)
  const netCashFlow = annualData.value.map(d => d.netCashFlow)
  const cumulativeCashFlow = annualData.value.map(d => d.cumulativeCashFlow)

  if (chartType.value === 'cumulative') {
    roiChart.setOption({
      tooltip: { trigger: 'axis', formatter: (params: any) => `Year ${params[0].axisValue}: $${formatNumber(params[0].value)}` },
      xAxis: { type: 'category', data: years, name: 'Year' },
      yAxis: { type: 'value', name: 'Cumulative Cash Flow ($)' },
      series: [{
        type: 'line', data: cumulativeCashFlow, smooth: true,
        lineStyle: { color: '#3b82f6', width: 3 },
        areaStyle: { opacity: 0.3, color: '#3b82f6' },
        symbol: 'circle', symbolSize: 8,
        label: { show: true, position: 'top', formatter: (p: any) => `$${formatNumber(p.value)}` }
      }]
    })
  } else {
    roiChart.setOption({
      tooltip: { trigger: 'axis', formatter: (params: any) => `Year ${params[0].axisValue}: $${formatNumber(params[0].value)}` },
      xAxis: { type: 'category', data: years.slice(1), name: 'Year' },
      yAxis: { type: 'value', name: 'Annual Cash Flow ($)' },
      series: [{
        type: 'bar', data: netCashFlow.slice(1),
        itemStyle: { borderRadius: [8, 8, 0, 0], color: '#10b981' },
        label: { show: true, position: 'top', formatter: (p: any) => `$${formatNumber(p.value)}` }
      }]
    })
  }
}

const initInvestmentSensitivityChart = () => {
  const canvas = document.getElementById('investmentSensitivityChart') as HTMLCanvasElement
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

  if (investmentSensitivityChart) investmentSensitivityChart.dispose()
  investmentSensitivityChart = echarts.init(canvas, null, { width: width, height: height, devicePixelRatio: pixelRatio })

  const variations = [-30, -20, -10, 0, 10, 20, 30]
  const npvValues = variations.map(varPct => {
    const adjInvestment = investment.value * (1 + varPct / 100)
    let npvValue = -adjInvestment
    for (let year = 1; year <= lifetime.value; year++) {
      npvValue += annualSavings.value / Math.pow(1 + discountRate.value / 100, year)
    }
    return npvValue / 1000
  })

  investmentSensitivityChart.setOption({
    tooltip: { trigger: 'axis', formatter: (params: any) => `Investment Change: ${params.axisValue}%\nNPV: $${params.value}k` },
    xAxis: { type: 'category', data: variations, name: 'Investment Change (%)' },
    yAxis: { type: 'value', name: 'NPV ($k)' },
    series: [{
      type: 'line', data: npvValues, smooth: true,
      lineStyle: { color: '#f59e0b', width: 3 },
      areaStyle: { opacity: 0.3, color: '#f59e0b' },
      symbol: 'circle', symbolSize: 8,
      label: { show: true, position: 'top', formatter: (p: any) => `$${p.value}k` }
    }]
  })
}

const initSavingsSensitivityChart = () => {
  const canvas = document.getElementById('savingsSensitivityChart') as HTMLCanvasElement
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

  if (savingsSensitivityChart) savingsSensitivityChart.dispose()
  savingsSensitivityChart = echarts.init(canvas, null, { width: width, height: height, devicePixelRatio: pixelRatio })

  const variations = [-30, -20, -10, 0, 10, 20, 30]
  const npvValues = variations.map(varPct => {
    const adjSavings = annualSavings.value * (1 + varPct / 100)
    let npvValue = -investment.value
    for (let year = 1; year <= lifetime.value; year++) {
      npvValue += adjSavings / Math.pow(1 + discountRate.value / 100, year)
    }
    return npvValue / 1000
  })

  savingsSensitivityChart.setOption({
    tooltip: { trigger: 'axis', formatter: (params: any) => `Savings Change: ${params.axisValue}%\nNPV: $${params.value}k` },
    xAxis: { type: 'category', data: variations, name: 'Annual Savings Change (%)' },
    yAxis: { type: 'value', name: 'NPV ($k)' },
    series: [{
      type: 'line', data: npvValues, smooth: true,
      lineStyle: { color: '#10b981', width: 3 },
      areaStyle: { opacity: 0.3, color: '#10b981' },
      symbol: 'circle', symbolSize: 8,
      label: { show: true, position: 'top', formatter: (p: any) => `$${p.value}k` }
    }]
  })
}

const refreshAllCharts = () => {
  setTimeout(() => {
    initROIChart()
    initInvestmentSensitivityChart()
    initSavingsSensitivityChart()
  }, 100)
}

// Watch for parameter changes
watch([investment, annualSavings, lifetime, discountRate, chartType, projectType], () => {
  refreshAllCharts()
})

// Window resize handler
let resizeTimer: ReturnType<typeof setTimeout> | null = null
const handleResize = () => {
  if (resizeTimer) clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => {
    if (roiChart) roiChart.resize()
    if (investmentSensitivityChart) investmentSensitivityChart.resize()
    if (savingsSensitivityChart) savingsSensitivityChart.resize()
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
          updateComparisonProjects()
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
  if (investmentSensitivityChart) investmentSensitivityChart.dispose()
  if (savingsSensitivityChart) savingsSensitivityChart.dispose()
})
</script>

<style scoped>
/* ==================== Loading Screen ==================== */
.roi-simulation-container {
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
.roi-simulation-main {
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

/* Project Section */
.project-section {
  margin-bottom: 24px;
}

.project-card {
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

/* Metrics Section */
.metrics-section {
  margin-bottom: 24px;
}

.metric-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  gap: 16px;
  align-items: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.metric-icon {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.metric-icon.blue { background: #eff6ff; color: #3b82f6; }
.metric-icon.green { background: #ecfdf5; color: #10b981; }
.metric-icon.orange { background: #fffbeb; color: #f59e0b; }
.metric-icon.purple { background: #f3e8ff; color: #8b5cf6; }

.metric-info {
  flex: 1;
}

.metric-label {
  display: block;
  font-size: 13px;
  color: #64748b;
  margin-bottom: 4px;
}

.metric-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

/* Chart Section */
.chart-section {
  margin-bottom: 24px;
}

.chart-card {
  border-radius: 20px;
  background: white;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.chart-container {
  width: 100%;
  min-height: 380px;
  position: relative;
}

/* Table Section */
.table-section {
  margin-bottom: 24px;
}

.table-card {
  border-radius: 20px;
  background: white;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.cashflow-table {
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

/* Comparison Section */
.comparison-section {
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

/* Recommendations Section */
.recommendations-section {
  margin-bottom: 24px;
}

.recommendations-card {
  border-radius: 20px;
  background: white;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.recommendations-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.recommendation-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 16px;
  transition: all 0.2s ease;
}

.recommendation-item:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.rec-status {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.rec-status.positive {
  background: #10b981;
  box-shadow: 0 0 8px #10b981;
}

.rec-status.neutral {
  background: #f59e0b;
  box-shadow: 0 0 8px #f59e0b;
}

.rec-status.negative {
  background: #ef4444;
  box-shadow: 0 0 8px #ef4444;
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

.rec-metrics span {
  color: #64748b;
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
  .roi-simulation-main { padding: 16px; }
}

@media (max-width: 768px) {
  .page-header { flex-direction: column; align-items: flex-start; gap: 16px; }
  .card-header { flex-direction: column; align-items: flex-start; gap: 12px; }
  .recommendation-item { flex-direction: column; }
  .rec-action { align-self: flex-end; }
  .action-buttons { flex-direction: column; }
  .action-buttons .el-button { width: 100%; }
}
</style>