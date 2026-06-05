<template>
  <!-- Loading Screen -->
  <div v-if="!isLoaded" class="loading-container">
    <div class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner">
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
        </div>
        <div class="loading-text">
          <span class="loading-title">ROI Calculator</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Investment Analysis Platform</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="roi-calculator-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Money /></el-icon>
          ROI Calculator
        </h1>
        <div class="page-subtitle">Calculate return on investment for data center optimization projects</div>
      </div>
      <div class="header-actions">
        <el-button @click="resetCalculator">
          <el-icon><RefreshLeft /></el-icon> Reset
        </el-button>
        <el-button type="primary" @click="exportReport">
          <el-icon><Download /></el-icon> Export Report
        </el-button>
      </div>
    </div>

    <!-- Main Two-Column Layout -->
    <div class="main-layout">
      <!-- Left: Calculator Inputs -->
      <div class="calculator-panel">
        <div class="panel-header">
          <span class="panel-title">Project Parameters</span>
          <span class="panel-subtitle">Enter your project details to calculate ROI</span>
        </div>

        <!-- Investment Section -->
        <div class="input-section">
          <div class="section-header">
            <span class="section-title">📊 Initial Investment</span>
          </div>
          <div class="input-group">
            <div class="input-row">
              <label>Equipment & Hardware Cost ($)</label>
              <el-input-number
                  v-model="inputs.equipmentCost"
                  :min="0"
                  :step="10000"
                  :precision="0"
                  @change="calculateROI"
              />
            </div>
            <div class="input-row">
              <label>Installation & Labor ($)</label>
              <el-input-number
                  v-model="inputs.installationCost"
                  :min="0"
                  :step="5000"
                  :precision="0"
                  @change="calculateROI"
              />
            </div>
            <div class="input-row">
              <label>Software & Licensing ($)</label>
              <el-input-number
                  v-model="inputs.softwareCost"
                  :min="0"
                  :step="5000"
                  :precision="0"
                  @change="calculateROI"
              />
            </div>
            <div class="input-row">
              <label>Training & Consulting ($)</label>
              <el-input-number
                  v-model="inputs.trainingCost"
                  :min="0"
                  :step="2000"
                  :precision="0"
                  @change="calculateROI"
              />
            </div>
          </div>
        </div>

        <!-- Savings Section -->
        <div class="input-section">
          <div class="section-header">
            <span class="section-title">💰 Annual Savings & Benefits</span>
          </div>
          <div class="input-group">
            <div class="input-row">
              <label>Energy Cost Savings ($/year)</label>
              <el-input-number
                  v-model="inputs.energySavings"
                  :min="0"
                  :step="10000"
                  :precision="0"
                  @change="calculateROI"
              />
            </div>
            <div class="input-row">
              <label>Maintenance Cost Reduction ($/year)</label>
              <el-input-number
                  v-model="inputs.maintenanceSavings"
                  :min="0"
                  :step="5000"
                  :precision="0"
                  @change="calculateROI"
              />
            </div>
            <div class="input-row">
              <label>Operational Efficiency Gains ($/year)</label>
              <el-input-number
                  v-model="inputs.operationalSavings"
                  :min="0"
                  :step="5000"
                  :precision="0"
                  @change="calculateROI"
              />
            </div>
            <div class="input-row">
              <label>Other Benefits ($/year)</label>
              <el-input-number
                  v-model="inputs.otherSavings"
                  :min="0"
                  :step="2000"
                  :precision="0"
                  @change="calculateROI"
              />
            </div>
          </div>
        </div>

        <!-- Financial Parameters -->
        <div class="input-section">
          <div class="section-header">
            <span class="section-title">💰 Financial Parameters</span>
          </div>
          <div class="input-group">
            <div class="input-row">
              <label>Discount Rate (%)</label>
              <el-slider v-model="inputs.discountRate" :min="0" :max="20" :step="0.5" @change="calculateROI" />
              <span class="slider-value">{{ inputs.discountRate }}%</span>
            </div>
            <div class="input-row">
              <label>Project Lifetime (years)</label>
              <el-slider v-model="inputs.projectLifetime" :min="1" :max="15" :step="1" @change="calculateROI" />
              <span class="slider-value">{{ inputs.projectLifetime }} years</span>
            </div>
          </div>
        </div>

        <!-- Scenario Buttons -->
        <div class="scenario-buttons">
          <span class="scenario-label">Quick Scenarios:</span>
          <el-button size="small" @click="loadScenario('cooling')">Cooling Optimization</el-button>
          <el-button size="small" @click="loadScenario('ups')">UPS Upgrade</el-button>
          <el-button size="small" @click="loadScenario('virtualization')">Server Virtualization</el-button>
          <el-button size="small" @click="loadScenario('lighting')">LED Lighting</el-button>
        </div>
      </div>

      <!-- Right: Results Panel -->
      <div class="results-panel">
        <div class="panel-header">
          <span class="panel-title">ROI Analysis Results</span>
          <span class="panel-subtitle">Based on your inputs</span>
        </div>

        <!-- Key Metrics -->
        <div class="key-metrics">
          <div class="metric-card">
            <div class="metric-icon green">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="metric-info">
              <div class="metric-value">{{ roiValue }}<span class="unit">%</span></div>
              <div class="metric-label">Return on Investment (ROI)</div>
            </div>
          </div>
          <div class="metric-card">
            <div class="metric-icon blue">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="metric-info">
              <div class="metric-value">{{ paybackPeriod }}<span class="unit">months</span></div>
              <div class="metric-label">Payback Period</div>
            </div>
          </div>
          <div class="metric-card">
            <div class="metric-icon orange">
              <el-icon><Money /></el-icon>
            </div>
            <div class="metric-info">
              <div class="metric-value">${{ formatNumber(npvValue) }}</div>
              <div class="metric-label">Net Present Value (NPV)</div>
            </div>
          </div>
          <div class="metric-card">
            <div class="metric-icon purple">
              <el-icon><DataLine /></el-icon>
            </div>
            <div class="metric-info">
              <div class="metric-value">{{ irrValue }}<span class="unit">%</span></div>
              <div class="metric-label">Internal Rate of Return (IRR)</div>
            </div>
          </div>
        </div>

        <!-- Total Investment & Savings -->
        <div class="summary-box">
          <div class="summary-item">
            <span class="summary-label">Total Initial Investment</span>
            <span class="summary-value">${{ formatNumber(totalInvestment) }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Annual Savings</span>
            <span class="summary-value">${{ formatNumber(annualSavings) }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Total Savings ({{ inputs.projectLifetime }} years)</span>
            <span class="summary-value">${{ formatNumber(totalSavingsOverLife) }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Net Profit</span>
            <span class="summary-value profit">${{ formatNumber(netProfit) }}</span>
          </div>
        </div>

        <!-- ROI Gauge Chart -->
        <div class="gauge-container">
          <div class="gauge-chart" ref="gaugeChart"></div>
        </div>

        <!-- Cash Flow Chart -->
        <div class="chart-container">
          <div class="chart-header">
            <span class="chart-title">Cash Flow Projection (5 Years)</span>
          </div>
          <div class="chart" ref="cashFlowChart"></div>
        </div>

        <!-- ROI Summary Text -->
        <div class="roi-summary" :class="roiClass">
          <el-icon><InfoFilled /></el-icon>
          <span>{{ roiRecommendation }}</span>
        </div>
      </div>
    </div>

    <!-- Comparison Table -->
    <div class="comparison-card">
      <div class="card-header">
        <span class="card-title">Scenario Comparison</span>
        <el-button size="small" @click="addToComparison">+ Compare Current</el-button>
      </div>
      <el-table :data="comparisonScenarios" stripe border style="width: 100%">
        <el-table-column prop="name" label="Scenario" />
        <el-table-column prop="investment" label="Investment" >
          <template #default="{ row }">${{ formatNumber(row.investment) }}</template>
        </el-table-column>
        <el-table-column prop="annualSavings" label="Annual Savings" >
          <template #default="{ row }">${{ formatNumber(row.annualSavings) }}</template>
        </el-table-column>
        <el-table-column prop="roi" label="ROI" >
          <template #default="{ row }">{{ row.roi }}%</template>
        </el-table-column>
        <el-table-column prop="payback" label="Payback" >
          <template #default="{ row }">{{ row.payback }} months</template>
        </el-table-column>
        <el-table-column prop="npv" label="NPV" >
          <template #default="{ row }">${{ formatNumber(row.npv) }}</template>
        </el-table-column>
        <el-table-column label="Action">
          <template #default="{ row }">
            <el-button type="danger" link size="small" @click="removeFromComparison(row)">Remove</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Money, RefreshLeft, Download, TrendCharts, Clock, DataLine, InfoFilled
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading ROI calculator...')

const loadingMessages = [
  'Loading ROI calculator...',
  'Initializing financial models...',
  'Preparing analysis tools...',
  'Almost ready...'
]

// ==================== Inputs ====================
const inputs = ref({
  equipmentCost: 250000,
  installationCost: 50000,
  softwareCost: 25000,
  trainingCost: 15000,
  energySavings: 120000,
  maintenanceSavings: 35000,
  operationalSavings: 25000,
  otherSavings: 10000,
  discountRate: 8,
  projectLifetime: 10
})

// ==================== Computed Values ====================
const totalInvestment = computed(() => {
  return inputs.value.equipmentCost + inputs.value.installationCost +
      inputs.value.softwareCost + inputs.value.trainingCost
})

const annualSavings = computed(() => {
  return inputs.value.energySavings + inputs.value.maintenanceSavings +
      inputs.value.operationalSavings + inputs.value.otherSavings
})

const totalSavingsOverLife = computed(() => {
  return annualSavings.value * inputs.value.projectLifetime
})

const netProfit = computed(() => {
  return totalSavingsOverLife.value - totalInvestment.value
})

const roiValue = computed(() => {
  if (totalInvestment.value === 0) return 0
  return Math.round((netProfit.value / totalInvestment.value) * 100)
})

const paybackPeriod = computed(() => {
  if (annualSavings.value === 0) return 0
  return Math.round((totalInvestment.value / annualSavings.value) * 12)
})

const npvValue = computed(() => {
  let npv = -totalInvestment.value
  const discountRateDecimal = inputs.value.discountRate / 100
  for (let year = 1; year <= inputs.value.projectLifetime; year++) {
    npv += annualSavings.value / Math.pow(1 + discountRateDecimal, year)
  }
  return Math.round(npv)
})

const irrValue = computed(() => {
  // Simplified IRR calculation
  if (totalInvestment.value === 0) return 0
  const ratio = annualSavings.value / totalInvestment.value
  let irr = ratio * 100
  return Math.round(Math.min(irr, 99))
})

const roiClass = computed(() => {
  if (roiValue.value >= 50) return 'excellent'
  if (roiValue.value >= 25) return 'good'
  if (roiValue.value >= 0) return 'fair'
  return 'poor'
})

const roiRecommendation = computed(() => {
  if (roiValue.value >= 100) return '🚀 Excellent investment opportunity! Strong ROI with rapid payback.'
  if (roiValue.value >= 50) return '✅ Good investment. Positive returns with acceptable payback period.'
  if (roiValue.value >= 25) return '📈 Moderate returns. Consider optimization opportunities.'
  if (roiValue.value >= 0) return '⚠️ Marginal returns. Review assumptions or explore alternatives.'
  return '❌ Negative returns. Not recommended without strategic justification.'
})

// ==================== Scenarios ====================
const comparisonScenarios = ref([
  { name: 'Cooling Optimization', investment: 85000, annualSavings: 45000, roi: 529, payback: 23, npv: 187000 },
  { name: 'UPS Upgrade', investment: 180000, annualSavings: 65000, roi: 361, payback: 33, npv: 265000 },
  { name: 'Server Virtualization', investment: 120000, annualSavings: 80000, roi: 667, payback: 18, npv: 380000 }
])

// ==================== Chart Refs ====================
const gaugeChart = ref<HTMLElement | null>(null)
const cashFlowChart = ref<HTMLElement | null>(null)

let gaugeChartInstance: echarts.ECharts | null = null
let cashFlowChartInstance: echarts.ECharts | null = null

// ==================== Methods ====================
const formatNumber = (num: number): string => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(0) + 'K'
  return num.toString()
}

const calculateROI = () => {
  nextTick(() => {
    updateGaugeChart()
    updateCashFlowChart()
  })
}

const updateGaugeChart = () => {
  if (!gaugeChart.value) return
  if (gaugeChartInstance) gaugeChartInstance.dispose()

  const roi = roiValue.value
  let color = '#ef4444'
  if (roi >= 100) color = '#22c55e'
  else if (roi >= 50) color = '#3b82f6'
  else if (roi >= 25) color = '#f59e0b'

  gaugeChartInstance = echarts.init(gaugeChart.value)
  gaugeChartInstance.setOption({
    series: [{
      type: 'gauge',
      center: ['50%', '50%'],
      radius: '70%',
      min: 0,
      max: 200,
      splitNumber: 8,
      progress: { show: true, width: 18, itemStyle: { color: color } },
      axisLine: { lineStyle: { width: 18, color: [[roi / 200, color], [1, '#e2e8f0']] } },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      pointer: { show: false },
      detail: {
        valueAnimation: true,
        fontSize: 32,
        fontWeight: 'bold',
        offsetCenter: [0, 0],
        formatter: (value: number) => `${Math.round(value)}%`
      },
      title: { show: false },
      data: [{ value: roi, name: 'ROI' }]
    }]
  })
}

const updateCashFlowChart = () => {
  if (!cashFlowChart.value) return
  if (cashFlowChartInstance) cashFlowChartInstance.dispose()

  const years = ['Year 0', 'Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 5']
  const cashFlow = [
    -totalInvestment.value,
    annualSavings.value,
    annualSavings.value,
    annualSavings.value,
    annualSavings.value,
    annualSavings.value
  ]

  cashFlowChartInstance = echarts.init(cashFlowChart.value)
  cashFlowChartInstance.setOption({
    tooltip: { trigger: 'axis', formatter: (params: any) => `${params[0].axisValue}<br/>Cash Flow: $${params[0].value.toLocaleString()}` },
    grid: { top: 30, left: 60, right: 30, bottom: 20 },
    xAxis: { type: 'category', data: years },
    yAxis: { type: 'value', name: 'Cash Flow ($)', axisLabel: { formatter: (v: number) => '$' + (v / 1000).toFixed(0) + 'k' } },
    series: [{
      type: 'bar',
      data: cashFlow,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => params.value >= 0 ? '#22c55e' : '#ef4444'
      },
      label: { show: true, position: 'top', formatter: (p: any) => '$' + (p.value / 1000).toFixed(0) + 'k' }
    }]
  })
}

const resetCalculator = () => {
  inputs.value = {
    equipmentCost: 250000,
    installationCost: 50000,
    softwareCost: 25000,
    trainingCost: 15000,
    energySavings: 120000,
    maintenanceSavings: 35000,
    operationalSavings: 25000,
    otherSavings: 10000,
    discountRate: 8,
    projectLifetime: 10
  }
  calculateROI()
  ElMessage.success('Calculator reset to default values')
}

const loadScenario = (scenario: string) => {
  switch(scenario) {
    case 'cooling':
      inputs.value = {
        equipmentCost: 85000, installationCost: 25000, softwareCost: 15000, trainingCost: 5000,
        energySavings: 55000, maintenanceSavings: 15000, operationalSavings: 10000, otherSavings: 5000,
        discountRate: 8, projectLifetime: 10
      }
      break
    case 'ups':
      inputs.value = {
        equipmentCost: 180000, installationCost: 35000, softwareCost: 10000, trainingCost: 8000,
        energySavings: 45000, maintenanceSavings: 20000, operationalSavings: 15000, otherSavings: 5000,
        discountRate: 8, projectLifetime: 12
      }
      break
    case 'virtualization':
      inputs.value = {
        equipmentCost: 120000, installationCost: 30000, softwareCost: 25000, trainingCost: 10000,
        energySavings: 50000, maintenanceSavings: 20000, operationalSavings: 25000, otherSavings: 5000,
        discountRate: 8, projectLifetime: 8
      }
      break
    case 'lighting':
      inputs.value = {
        equipmentCost: 35000, installationCost: 15000, softwareCost: 5000, trainingCost: 2000,
        energySavings: 18000, maintenanceSavings: 5000, operationalSavings: 3000, otherSavings: 2000,
        discountRate: 8, projectLifetime: 10
      }
      break
  }
  calculateROI()
  ElMessage.success(`Loaded ${scenario} scenario`)
}

const addToComparison = () => {
  const newScenario = {
    name: 'Current Project',
    investment: totalInvestment.value,
    annualSavings: annualSavings.value,
    roi: roiValue.value,
    payback: paybackPeriod.value,
    npv: npvValue.value
  }
  comparisonScenarios.value.push(newScenario)
  ElMessage.success('Added to comparison')
}

const removeFromComparison = (scenario: any) => {
  const index = comparisonScenarios.value.indexOf(scenario)
  if (index !== -1) {
    comparisonScenarios.value.splice(index, 1)
    ElMessage.success('Removed from comparison')
  }
}

const exportReport = () => {
  ElMessage.success('Export started')
  setTimeout(() => {
    ElMessage.success('ROI report exported')
  }, 1500)
}

// ==================== Watch for input changes ====================
watch([totalInvestment, annualSavings], () => {
  calculateROI()
})

// ==================== Loading Animation ====================
const startLoading = () => {
  let progress = 0
  let messageIndex = 0

  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 600)

  const progressInterval = setInterval(() => {
    if (progress < 90) {
      progress += Math.random() * 12
      loadingProgress.value = Math.min(progress, 90)
    }
  }, 100)

  setTimeout(() => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'

    setTimeout(() => {
      isLoaded.value = true
      nextTick(() => {
        updateGaugeChart()
        updateCashFlowChart()
      })
    }, 500)
  }, 2200)
}

onMounted(() => {
  startLoading()
})
</script>

<style scoped>
* {
  scrollbar-width: thin;
}
*::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
*::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}
*::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

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

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

/* ==================== Main Page ==================== */
.roi-calculator-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 24px;
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Main Layout */
.main-layout {
  display: flex;
  gap: 24px;
  margin-bottom: 24px;
}

.calculator-panel {
  flex: 1;
  background: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.results-panel {
  flex: 1;
  background: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.panel-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eef2f8;
}

.panel-title {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  display: block;
  margin-bottom: 4px;
}

.panel-subtitle {
  font-size: 13px;
  color: #64748b;
}

/* Input Sections */
.input-section {
  margin-bottom: 24px;
}

.section-header {
  margin-bottom: 16px;
}

.section-title {
  font-weight: 600;
  font-size: 15px;
  color: #1e293b;
}

.input-group {
  background: #f8fafc;
  border-radius: 16px;
  padding: 16px;
}

.input-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.input-row:last-child {
  margin-bottom: 0;
}

.input-row label {
  font-size: 13px;
  color: #475569;
  width: 45%;
}

.input-row .el-input-number {
  width: 45%;
}

.input-row .el-slider {
  width: 35%;
  margin: 0 12px;
}

.slider-value {
  width: 45px;
  font-size: 13px;
  color: #3b82f6;
  font-weight: 500;
}

/* Scenario Buttons */
.scenario-buttons {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #eef2f8;
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.scenario-label {
  font-size: 13px;
  color: #64748b;
}

/* Key Metrics */
.key-metrics {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.metric-card {
  background: #f8fafc;
  border-radius: 16px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 14px;
  transition: all 0.2s;
}

.metric-card:hover {
  transform: translateY(-2px);
  background: #f1f5f9;
}

.metric-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
}

.metric-icon.green { background: #dcfce7; color: #22c55e; }
.metric-icon.blue { background: #eef2ff; color: #3b82f6; }
.metric-icon.orange { background: #fef3c7; color: #f59e0b; }
.metric-icon.purple { background: #f3e8ff; color: #8b5cf6; }

.metric-info {
  flex: 1;
}

.metric-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.metric-value .unit {
  font-size: 12px;
  font-weight: normal;
  color: #64748b;
  margin-left: 2px;
}

.metric-label {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
}

/* Summary Box */
.summary-box {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 24px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.summary-item:last-child {
  border-bottom: none;
}

.summary-label {
  font-size: 13px;
  color: #94a3b8;
}

.summary-value {
  font-size: 18px;
  font-weight: 700;
  color: white;
}

.summary-value.profit {
  color: #4ade80;
}

/* Gauge Chart */
.gauge-container {
  margin-bottom: 24px;
}

.gauge-chart {
  height: 200px;
  width: 100%;
}

/* Cash Flow Chart */
.chart-container {
  margin-bottom: 24px;
}

.chart-header {
  margin-bottom: 16px;
}

.chart-title {
  font-weight: 600;
  font-size: 15px;
  color: #1e293b;
}

.chart {
  height: 240px;
  width: 100%;
}

/* ROI Summary */
.roi-summary {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-radius: 12px;
  font-size: 13px;
}

.roi-summary.excellent { background: #dcfce7; color: #16a34a; }
.roi-summary.good { background: #eef2ff; color: #2563eb; }
.roi-summary.fair { background: #fef3c7; color: #d97706; }
.roi-summary.poor { background: #fee2e2; color: #dc2626; }

/* Comparison Card */
.comparison-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
}

/* Responsive */
@media (max-width: 1000px) {
  .main-layout {
    flex-direction: column;
  }

  .key-metrics {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .key-metrics {
    grid-template-columns: 1fr;
  }

  .input-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .input-row label,
  .input-row .el-input-number,
  .input-row .el-slider {
    width: 100%;
  }

  .scenario-buttons {
    justify-content: center;
  }
}
</style>