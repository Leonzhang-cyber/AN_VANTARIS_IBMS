<template>
  <div class="free-cooling-simulation-container">
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
            <span class="loading-title">Loading Free Cooling Simulation</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Free Cooling Potential Analysis</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="free-cooling-simulation-main">
      <!-- Page Header -->
      <div class="page-header">
        <div>
          <h1 class="page-title">Free Cooling Simulation</h1>
          <p class="page-subtitle">Analyze free cooling potential and optimize economizer usage</p>
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
          <el-button @click="applyRecommendations">
            <el-icon><MagicStick /></el-icon>
            Apply Recommendations
          </el-button>
        </div>
      </div>

      <!-- Alert Banner -->
      <div v-if="highFreeCoolingPotential" class="alert-banner success">
        <el-icon><CircleCheck /></el-icon>
        <span>High free cooling potential detected! {{ freeCoolingHours }} hours available annually.</span>
        <el-button size="small" type="success" @click="optimizeNow">Optimize Now</el-button>
      </div>

      <!-- Overview Cards -->
      <div class="overview-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="overview-card">
              <div class="card-icon blue">
                <el-icon><Clock /></el-icon>
              </div>
              <div class="card-info">
                <span class="card-label">Free Cooling Hours</span>
                <span class="card-value">{{ freeCoolingHours }} hrs/year</span>
                <el-progress :percentage="(freeCoolingHours / 8760) * 100" :stroke-width="6" color="#3b82f6" :show-text="false" />
                <span class="card-hint">{{ ((freeCoolingHours / 8760) * 100).toFixed(1) }}% of year</span>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="overview-card">
              <div class="card-icon green">
                <el-icon><DataLine /></el-icon>
              </div>
              <div class="card-info">
                <span class="card-label">Energy Savings</span>
                <span class="card-value">{{ formatNumber(energySavings) }} kWh/year</span>
                <el-progress :percentage="(energySavings / totalCoolingEnergy) * 100" :stroke-width="6" color="#10b981" :show-text="false" />
                <span class="card-hint">{{ ((energySavings / totalCoolingEnergy) * 100).toFixed(1) }}% reduction</span>
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
                <span class="card-hint">ROI: {{ roiMonths }} months</span>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="overview-card">
              <div class="card-icon purple">
                <el-icon><Sunny /></el-icon>
              </div>
              <div class="card-info">
                <span class="card-label">Carbon Reduction</span>
                <span class="card-value">{{ carbonReduction }} tCO₂e/year</span>
                <el-progress :percentage="(carbonReduction / 500) * 100" :stroke-width="6" color="#8b5cf6" :show-text="false" />
                <span class="card-hint">Equivalent to {{ treesPlanted }} trees</span>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- Simulation Parameters -->
      <div class="simulation-params-section">
        <el-card class="params-card" shadow="hover">
          <div class="card-header">
            <div class="card-title">
              <el-icon><Setting /></el-icon>
              <span>Simulation Parameters</span>
            </div>
            <el-button size="small" @click="resetParameters">Reset to Default</el-button>
          </div>
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="param-group">
                <label>Location / Climate Zone</label>
                <el-select v-model="climateZone" placeholder="Select Zone" @change="updateClimateData">
                  <el-option label="San Francisco, CA (Cool Marine)" value="sf" />
                  <el-option label="New York, NY (Temperate)" value="ny" />
                  <el-option label="Chicago, IL (Cold)" value="chicago" />
                  <el-option label="Atlanta, GA (Warm Humid)" value="atlanta" />
                  <el-option label="Phoenix, AZ (Hot Arid)" value="phoenix" />
                  <el-option label="Custom" value="custom" />
                </el-select>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="param-group">
                <label>Free Cooling Type</label>
                <el-select v-model="freeCoolingType" placeholder="Select Type">
                  <el-option label="Air-Side Economizer" value="air" />
                  <el-option label="Water-Side Economizer" value="water" />
                  <el-option label="Hybrid (Air + Water)" value="hybrid" />
                </el-select>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="param-group">
                <label>Supply Air Setpoint (°C)</label>
                <el-input-number v-model="supplySetpoint" :min="18" :max="27" :step="0.5" style="width: 100%" />
              </div>
            </el-col>
            <el-col :span="6">
              <div class="param-group">
                <label>Return Air Temp (°C)</label>
                <el-input-number v-model="returnTemp" :min="24" :max="35" :step="0.5" style="width: 100%" />
              </div>
            </el-col>
          </el-row>
          <el-row :gutter="20" style="margin-top: 16px">
            <el-col :span="6">
              <div class="param-group">
                <label>Economizer Enable Temp (°C)</label>
                <el-input-number v-model="economizerEnableTemp" :min="5" :max="25" :step="0.5" style="width: 100%" />
              </div>
            </el-col>
            <el-col :span="6">
              <div class="param-group">
                <label>Economizer Disable Temp (°C)</label>
                <el-input-number v-model="economizerDisableTemp" :min="10" :max="30" :step="0.5" style="width: 100%" />
              </div>
            </el-col>
            <el-col :span="6">
              <div class="param-group">
                <label>Humidity Limit (%)</label>
                <el-input-number v-model="humidityLimit" :min="30" :max="80" :step="5" style="width: 100%" />
              </div>
            </el-col>
            <el-col :span="6">
              <div class="param-group">
                <label>Cooling Load (kW)</label>
                <el-input-number v-model="coolingLoad" :min="100" :max="5000" :step="50" style="width: 100%" />
              </div>
            </el-col>
          </el-row>
        </el-card>
      </div>

      <!-- Free Cooling Hours Chart -->
      <div class="hours-section">
        <el-card class="hours-card" shadow="hover">
          <div class="card-header">
            <div class="card-title">
              <el-icon><TrendCharts /></el-icon>
              <span>Monthly Free Cooling Hours Analysis</span>
            </div>
            <el-radio-group v-model="hoursViewType" size="small">
              <el-radio-button label="hours">Hours</el-radio-button>
              <el-radio-button label="percentage">Percentage</el-radio-button>
            </el-radio-group>
          </div>
          <div class="chart-container">
            <canvas id="freeCoolingHoursChart"></canvas>
          </div>
        </el-card>
      </div>

      <!-- Energy Savings Analysis -->
      <div class="savings-section">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card class="savings-card" shadow="hover">
              <div class="card-header">
                <div class="card-title">
                  <el-icon><DataLine /></el-icon>
                  <span>Energy Savings by Month</span>
                </div>
              </div>
              <div class="chart-container">
                <canvas id="energySavingsChart"></canvas>
              </div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card class="savings-card" shadow="hover">
              <div class="card-header">
                <div class="card-title">
                  <el-icon><PieChart /></el-icon>
                  <span>Savings Breakdown</span>
                </div>
              </div>
              <div class="chart-container">
                <canvas id="savingsBreakdownChart"></canvas>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Temperature Bin Analysis -->
      <div class="bin-section">
        <el-card class="bin-card" shadow="hover">
          <div class="card-header">
            <div class="card-title">
              <el-icon><Grid /></el-icon>
              <span>Temperature Bin Analysis</span>
            </div>
          </div>
          <div class="chart-container">
            <canvas id="temperatureBinChart"></canvas>
          </div>
        </el-card>
      </div>

      <!-- Economizer Performance -->
      <div class="economizer-section">
        <el-row :gutter="20">
          <el-col :span="16">
            <el-card class="economizer-card" shadow="hover">
              <div class="card-header">
                <div class="card-title">
                  <el-icon><Monitor /></el-icon>
                  <span>Economizer Performance Curve</span>
                </div>
              </div>
              <div class="chart-container">
                <canvas id="economizerCurveChart"></canvas>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card class="recommendations-card" shadow="hover">
              <div class="card-header">
                <div class="card-title">
                  <el-icon><Setting /></el-icon>
                  <span>Optimization Recommendations</span>
                </div>
              </div>
              <div class="recommendations-list">
                <div v-for="rec in recommendations" :key="rec.id" class="recommendation-item">
                  <div class="rec-header">
                    <el-icon :color="rec.priority === 'high' ? '#ef4444' : '#f59e0b'">
                      <WarningFilled v-if="rec.priority === 'high'" />
                      <InfoFilled v-else />
                    </el-icon>
                    <span class="rec-title">{{ rec.title }}</span>
                  </div>
                  <p class="rec-description">{{ rec.description }}</p>
                  <div class="rec-impact">
                    <span>Potential Savings: {{ rec.savings }}</span>
                    <el-button type="primary" link size="small" @click="applyRecommendation(rec)">Apply</el-button>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Comparison Table -->
      <div class="comparison-section">
        <div class="section-header">
          <h3>Free Cooling Comparison by Location</h3>
        </div>
        <el-table :data="locationComparison" stripe class="comparison-table">
          <el-table-column prop="location" label="Location"  />
          <el-table-column prop="freeCoolingHours" label="Free Cooling Hours" >
            <template #default="{ row }">
              <el-progress :percentage="(row.freeCoolingHours / 8760) * 100" :stroke-width="8" :format="() => `${row.freeCoolingHours} hrs`" />
            </template>
          </el-table-column>
          <el-table-column prop="energySavings" label="Energy Savings (kWh)" >
            <template #default="{ row }">
              {{ formatNumber(row.energySavings) }}
            </template>
          </el-table-column>
          <el-table-column prop="costSavings" label="Cost Savings ($)" >
            <template #default="{ row }">
              ${{ formatNumber(row.costSavings) }}
            </template>
          </el-table-column>
          <el-table-column prop="carbonReduction" label="Carbon Reduction (tCO₂e)"  />
          <el-table-column prop="roi" label="ROI (months)" width="100">
            <template #default="{ row }">
              <el-tag :type="row.roi <= 12 ? 'success' : 'warning'" size="small">{{ row.roi }} months</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Action Buttons -->
      <div class="action-buttons">
        <el-button type="primary" size="large" @click="generateDetailedReport">
          <el-icon><Document /></el-icon>
          Generate Detailed Report
        </el-button>
        <el-button size="large" @click="scheduleImplementation">
          <el-icon><Calendar /></el-icon>
          Schedule Implementation
        </el-button>
        <el-button size="large" @click="compareScenarios">
          <el-icon><TrendCharts /></el-icon>
          Compare Scenarios
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
  Cpu, Download, MagicStick, Clock, DataLine, Coin, Sunny,
  Setting, TrendCharts, PieChart, Grid, Monitor, Document, Calendar,
  CircleCheck, WarningFilled, InfoFilled
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading free cooling simulation...')

// ==================== Simulation Parameters ====================
const climateZone = ref('ny')
const freeCoolingType = ref('air')
const supplySetpoint = ref(22)
const returnTemp = ref(28)
const economizerEnableTemp = ref(18)
const economizerDisableTemp = ref(24)
const humidityLimit = ref(60)
const coolingLoad = ref(1000)
const hoursViewType = ref('hours')

// Climate data for different locations
const climateData: Record<string, { name: string, monthlyTemps: number[] }> = {
  sf: { name: 'San Francisco', monthlyTemps: [12, 13, 14, 15, 16, 17, 18, 18, 18, 17, 14, 12] },
  ny: { name: 'New York', monthlyTemps: [0, 1, 5, 11, 17, 22, 25, 24, 20, 14, 8, 3] },
  chicago: { name: 'Chicago', monthlyTemps: [-3, -1, 4, 10, 16, 21, 24, 23, 19, 12, 5, 0] },
  atlanta: { name: 'Atlanta', monthlyTemps: [7, 9, 13, 17, 22, 26, 28, 27, 24, 18, 12, 8] },
  phoenix: { name: 'Phoenix', monthlyTemps: [12, 14, 18, 22, 28, 33, 36, 35, 31, 24, 17, 12] },
  custom: { name: 'Custom', monthlyTemps: [5, 6, 10, 15, 20, 25, 28, 27, 22, 16, 10, 6] }
}

// Current monthly temperatures
const monthlyTemps = ref<number[]>([...climateData.ny.monthlyTemps])

// Computed metrics
const freeCoolingHours = computed(() => {
  let totalHours = 0
  const daysPerMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
  for (let i = 0; i < 12; i++) {
    const temp = monthlyTemps.value[i]
    if (temp >= economizerEnableTemp.value && temp <= economizerDisableTemp.value) {
      totalHours += daysPerMonth[i] * 24
    }
  }
  return totalHours
})

const freeCoolingPercentage = computed(() => (freeCoolingHours.value / 8760) * 100)

const totalCoolingEnergy = computed(() => {
  // Assume 0.5 kW per kW of cooling load for compressor operation
  return coolingLoad.value * 8760 * 0.5
})

const energySavings = computed(() => {
  // Savings proportional to free cooling hours
  return totalCoolingEnergy.value * (freeCoolingHours.value / 8760) * 0.7
})

const costSavings = computed(() => {
  // Assume $0.12 per kWh
  return energySavings.value * 0.12
})

const carbonReduction = computed(() => {
  // Assume 0.4 kg CO2 per kWh
  return energySavings.value * 0.0004
})

const treesPlanted = computed(() => {
  return Math.round(carbonReduction.value / 0.02) // 0.02 tCO2 per tree per year
})

const roiMonths = computed(() => {
  // Assume implementation cost of $50,000
  const implementationCost = 50000
  if (costSavings.value === 0) return 0
  return Math.round(implementationCost / (costSavings.value / 12))
})

const highFreeCoolingPotential = computed(() => freeCoolingPercentage.value > 30)

// Recommendations
const recommendations = ref([
  { id: 1, title: 'Increase Supply Air Setpoint', description: 'Raising supply air temperature by 2°C can increase free cooling hours by 15%', savings: '85,000 kWh/year', priority: 'high' },
  { id: 2, title: 'Widen Economizer Deadband', description: 'Expand the economizer enable/disable temperature range', savings: '45,000 kWh/year', priority: 'medium' },
  { id: 3, title: 'Install Air-Side Economizer', description: 'Implement air-side economizer for current location', savings: '120,000 kWh/year', priority: 'high' },
  { id: 4, title: 'Optimize Humidity Control', description: 'Adjust humidity limits to maximize free cooling hours', savings: '25,000 kWh/year', priority: 'low' }
])

// Location comparison data
const locationComparison = ref([
  { location: 'San Francisco', freeCoolingHours: 4850, energySavings: 1250000, costSavings: 150000, carbonReduction: 500, roi: 4 },
  { location: 'New York', freeCoolingHours: 3650, energySavings: 950000, costSavings: 114000, carbonReduction: 380, roi: 6 },
  { location: 'Chicago', freeCoolingHours: 3950, energySavings: 1020000, costSavings: 122400, carbonReduction: 408, roi: 5 },
  { location: 'Atlanta', freeCoolingHours: 2200, energySavings: 570000, costSavings: 68400, carbonReduction: 228, roi: 9 },
  { location: 'Phoenix', freeCoolingHours: 1200, energySavings: 310000, costSavings: 37200, carbonReduction: 124, roi: 16 }
])

// Helper functions
const formatNumber = (num: number) => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k'
  return num.toString()
}

const updateClimateData = () => {
  monthlyTemps.value = [...climateData[climateZone.value].monthlyTemps]
  refreshAllCharts()
}

const resetParameters = () => {
  freeCoolingType.value = 'air'
  supplySetpoint.value = 22
  returnTemp.value = 28
  economizerEnableTemp.value = 18
  economizerDisableTemp.value = 24
  humidityLimit.value = 60
  coolingLoad.value = 1000
  climateZone.value = 'ny'
  updateClimateData()
  ElMessage.success('Parameters reset to default values')
}

const runSimulation = () => {
  ElMessage.success('Simulation completed. Results updated.')
  refreshAllCharts()
}

const exportReport = () => {
  ElMessage.success('Report export started')
}

const applyRecommendations = () => {
  ElMessage.success('Recommendations applied to current configuration')
}

const optimizeNow = () => {
  ElMessage.success('Optimization started. Results will be available shortly.')
}

const applyRecommendation = (rec: any) => {
  ElMessage.success(`Applied: ${rec.title}`)
}

const generateDetailedReport = () => {
  ElMessage.success('Detailed report generation started')
}

const scheduleImplementation = () => {
  ElMessage.info('Implementation scheduling interface will open')
}

const compareScenarios = () => {
  ElMessage.info('Scenario comparison tool will open')
}

// Chart instances
let freeCoolingHoursChart: echarts.ECharts | null = null
let energySavingsChart: echarts.ECharts | null = null
let savingsBreakdownChart: echarts.ECharts | null = null
let temperatureBinChart: echarts.ECharts | null = null
let economizerCurveChart: echarts.ECharts | null = null

// Chart initialization
const initFreeCoolingHoursChart = () => {
  const canvas = document.getElementById('freeCoolingHoursChart') as HTMLCanvasElement
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

  if (freeCoolingHoursChart) freeCoolingHoursChart.dispose()
  freeCoolingHoursChart = echarts.init(canvas, null, { width: width, height: height, devicePixelRatio: pixelRatio })

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const daysPerMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

  let freeHours: number[] = []
  let totalHours: number[] = []

  for (let i = 0; i < 12; i++) {
    const temp = monthlyTemps.value[i]
    const isFreeCooling = temp >= economizerEnableTemp.value && temp <= economizerDisableTemp.value
    const eligibleHours = isFreeCooling ? daysPerMonth[i] * 24 : 0
    freeHours.push(eligibleHours)
    totalHours.push(daysPerMonth[i] * 24)
  }

  if (hoursViewType.value === 'hours') {
    freeCoolingHoursChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Free Cooling Hours', 'Total Hours'], bottom: 0, left: 'center' },
      grid: { top: 40, left: 60, right: 40, bottom: 50, containLabel: true },
      xAxis: { type: 'category', data: months, axisLabel: { fontSize: 11 } },
      yAxis: { type: 'value', name: 'Hours' },
      series: [
        { name: 'Free Cooling Hours', type: 'bar', data: freeHours, itemStyle: { color: '#10b981', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top', formatter: '{c} hrs' } },
        { name: 'Total Hours', type: 'bar', data: totalHours, itemStyle: { color: '#e2e8f0', borderRadius: [8, 8, 0, 0] } }
      ]
    })
  } else {
    const percentages = freeHours.map((h, i) => (h / totalHours[i]) * 100)
    freeCoolingHoursChart.setOption({
      tooltip: { trigger: 'axis', formatter: '{b}: {c}%' },
      xAxis: { type: 'category', data: months },
      yAxis: { type: 'value', name: 'Free Cooling %', max: 100 },
      series: [{
        type: 'line', data: percentages, smooth: true,
        lineStyle: { color: '#10b981', width: 3 },
        areaStyle: { opacity: 0.3, color: '#10b981' },
        symbol: 'circle', symbolSize: 8,
        label: { show: true, position: 'top', formatter: '{c}%' }
      }]
    })
  }
}

const initEnergySavingsChart = () => {
  const canvas = document.getElementById('energySavingsChart') as HTMLCanvasElement
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

  if (energySavingsChart) energySavingsChart.dispose()
  energySavingsChart = echarts.init(canvas, null, { width: width, height: height, devicePixelRatio: pixelRatio })

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const daysPerMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
  const monthlySavings: number[] = []

  for (let i = 0; i < 12; i++) {
    const temp = monthlyTemps.value[i]
    const isFreeCooling = temp >= economizerEnableTemp.value && temp <= economizerDisableTemp.value
    if (isFreeCooling) {
      const hours = daysPerMonth[i] * 24
      const savings = coolingLoad.value * hours * 0.5 * 0.7
      monthlySavings.push(savings)
    } else {
      monthlySavings.push(0)
    }
  }

  energySavingsChart.setOption({
    tooltip: { trigger: 'axis', formatter: '{b}: {c} kWh' },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'Energy Savings (kWh)' },
    series: [{
      type: 'bar', data: monthlySavings,
      itemStyle: { borderRadius: [8, 8, 0, 0], color: '#f59e0b' },
      label: { show: true, position: 'top', formatter: (p: any) => Math.round(p.value / 1000) + 'k kWh' }
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

  const fanEnergy = energySavings.value * 0.3
  const compressorEnergy = energySavings.value * 0.5
  const pumpEnergy = energySavings.value * 0.2

  savingsBreakdownChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c} kWh)' },
    legend: { top: 'bottom' },
    series: [{
      type: 'pie', radius: ['45%', '70%'],
      data: [
        { value: compressorEnergy, name: 'Compressor Savings', itemStyle: { color: '#3b82f6' } },
        { value: fanEnergy, name: 'Fan Savings', itemStyle: { color: '#10b981' } },
        { value: pumpEnergy, name: 'Pump Savings', itemStyle: { color: '#f59e0b' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  })
}

const initTemperatureBinChart = () => {
  const canvas = document.getElementById('temperatureBinChart') as HTMLCanvasElement
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

  if (temperatureBinChart) temperatureBinChart.dispose()
  temperatureBinChart = echarts.init(canvas, null, { width: width, height: height, devicePixelRatio: pixelRatio })

  const bins = ['<0°C', '0-5°C', '5-10°C', '10-15°C', '15-20°C', '20-25°C', '25-30°C', '>30°C']
  const hoursPerBin = [350, 450, 650, 850, 1200, 1850, 2200, 1100]
  const freeCoolingBins = [0, 350, 650, 850, 1000, 800, 0, 0]

  temperatureBinChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Total Hours', 'Free Cooling Eligible'], bottom: 0, left: 'center' },
    xAxis: { type: 'category', data: bins, axisLabel: { rotate: 30 } },
    yAxis: { type: 'value', name: 'Hours per Year' },
    series: [
      { name: 'Total Hours', type: 'bar', data: hoursPerBin, itemStyle: { color: '#e2e8f0', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top', formatter: '{c} hrs' } },
      { name: 'Free Cooling Eligible', type: 'bar', data: freeCoolingBins, itemStyle: { color: '#10b981', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top', formatter: '{c} hrs' } }
    ]
  })
}

const initEconomizerCurveChart = () => {
  const canvas = document.getElementById('economizerCurveChart') as HTMLCanvasElement
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

  if (economizerCurveChart) economizerCurveChart.dispose()
  economizerCurveChart = echarts.init(canvas, null, { width: width, height: height, devicePixelRatio: pixelRatio })

  const temps = Array.from({ length: 20 }, (_, i) => i + 5)
  const freeCoolingPotential = temps.map(t => {
    if (t < economizerEnableTemp.value) return 0
    if (t > economizerDisableTemp.value) return 0
    return 100 - (t - economizerEnableTemp.value) * 5
  })

  economizerCurveChart.setOption({
    tooltip: { trigger: 'axis', formatter: 'Outside Temp: {b}°C\nFree Cooling Potential: {c}%' },
    xAxis: { type: 'category', data: temps, name: 'Outside Temperature (°C)' },
    yAxis: { type: 'value', name: 'Free Cooling Potential (%)', max: 100 },
    series: [{
      type: 'line', data: freeCoolingPotential, smooth: true,
      lineStyle: { color: '#3b82f6', width: 3 },
      areaStyle: { opacity: 0.3, color: '#3b82f6' },
      symbol: 'circle', symbolSize: 6,
      markArea: {
        data: [[{ xAxis: economizerEnableTemp.value }, { xAxis: economizerDisableTemp.value }]],
        itemStyle: { color: 'rgba(16, 185, 129, 0.1)' }
      }
    }]
  })
}

const refreshAllCharts = () => {
  setTimeout(() => {
    initFreeCoolingHoursChart()
    initEnergySavingsChart()
    initSavingsBreakdownChart()
    initTemperatureBinChart()
    initEconomizerCurveChart()
  }, 100)
}

// Watch for parameter changes
watch([economizerEnableTemp, economizerDisableTemp, coolingLoad, supplySetpoint, freeCoolingType, hoursViewType], () => {
  refreshAllCharts()
})

// Window resize handler
let resizeTimer: ReturnType<typeof setTimeout> | null = null
const handleResize = () => {
  if (resizeTimer) clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => {
    if (freeCoolingHoursChart) freeCoolingHoursChart.resize()
    if (energySavingsChart) energySavingsChart.resize()
    if (savingsBreakdownChart) savingsBreakdownChart.resize()
    if (temperatureBinChart) temperatureBinChart.resize()
    if (economizerCurveChart) economizerCurveChart.resize()
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
  if (freeCoolingHoursChart) freeCoolingHoursChart.dispose()
  if (energySavingsChart) energySavingsChart.dispose()
  if (savingsBreakdownChart) savingsBreakdownChart.dispose()
  if (temperatureBinChart) temperatureBinChart.dispose()
  if (economizerCurveChart) economizerCurveChart.dispose()
})
</script>

<style scoped>
/* ==================== Loading Screen ==================== */
.free-cooling-simulation-container {
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
.free-cooling-simulation-main {
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

/* Hours Section */
.hours-section {
  margin-bottom: 24px;
}

.hours-card {
  border-radius: 20px;
  background: white;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.chart-container {
  width: 100%;
  min-height: 350px;
  position: relative;
}

/* Savings Section */
.savings-section {
  margin-bottom: 24px;
}

.savings-card {
  border-radius: 20px;
  background: white;
  padding: 20px;
  height: 100%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

/* Bin Section */
.bin-section {
  margin-bottom: 24px;
}

.bin-card {
  border-radius: 20px;
  background: white;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

/* Economizer Section */
.economizer-section {
  margin-bottom: 24px;
}

.economizer-card {
  border-radius: 20px;
  background: white;
  padding: 20px;
  height: 100%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.recommendations-card {
  border-radius: 20px;
  background: white;
  padding: 20px;
  height: 100%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.recommendation-item {
  padding: 12px;
  background: #f8fafc;
  border-radius: 12px;
}

.rec-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.rec-title {
  font-weight: 600;
  color: #1e293b;
}

.rec-description {
  font-size: 12px;
  color: #64748b;
  margin: 0 0 8px 0;
}

.rec-impact {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}

.rec-impact span {
  color: #10b981;
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
  .free-cooling-simulation-main { padding: 16px; }
}

@media (max-width: 768px) {
  .page-header { flex-direction: column; align-items: flex-start; gap: 16px; }
  .action-buttons { flex-direction: column; }
  .action-buttons .el-button { width: 100%; }
  .card-value { font-size: 20px; }
}
</style>