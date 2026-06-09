<template>
  <div class="carbon-optimization-container">
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
            <span class="loading-title">Loading Carbon Optimization</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Carbon Emission Management & Optimization</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="carbon-optimization-main">
      <!-- Page Header -->
      <div class="page-header">
        <div>
          <h1 class="page-title">Carbon Optimization</h1>
          <p class="page-subtitle">Monitor, analyze and reduce carbon emissions</p>
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
          <el-button @click="setCarbonTargets">
            <el-icon><Setting /></el-icon>
            Set Targets
          </el-button>
        </div>
      </div>

      <!-- Alert Banner -->
      <div v-if="carbonAlert" class="alert-banner" :class="alertSeverity">
        <el-icon><WarningFilled /></el-icon>
        <span>{{ alertMessage }}</span>
        <el-button size="small" :type="alertSeverity === 'critical' ? 'danger' : 'warning'" @click="viewCarbonDetails">
          View Details
        </el-button>
      </div>

      <!-- Overview Cards -->
      <div class="overview-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="overview-card">
              <div class="card-icon green">
                <el-icon><DataLine /></el-icon>
              </div>
              <div class="card-info">
                <span class="card-label">Total Carbon (YTD)</span>
                <span class="card-value">{{ totalCarbon }} tCO₂e</span>
                <el-progress :percentage="(totalCarbon / annualTarget) * 100" :stroke-width="6" :color="getProgressColor((totalCarbon / annualTarget) * 100)" :show-text="false" />
                <span class="card-hint">Annual Target: {{ annualTarget }} tCO₂e</span>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="overview-card">
              <div class="card-icon blue">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="card-info">
                <span class="card-label">Carbon Intensity</span>
                <span class="card-value">{{ carbonIntensity }} gCO₂e/kWh</span>
                <el-progress :percentage="100 - (carbonIntensity / targetIntensity) * 100" :stroke-width="6" color="#3b82f6" :show-text="false" />
                <span class="card-hint">Target: {{ targetIntensity }} gCO₂e/kWh</span>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="overview-card">
              <div class="card-icon orange">
                <el-icon><Sunny /></el-icon>
              </div>
              <div class="card-info">
                <span class="card-label">Renewable Energy</span>
                <span class="card-value">{{ renewablePercentage }}%</span>
                <el-progress :percentage="renewablePercentage" :stroke-width="6" color="#f59e0b" :show-text="false" />
                <span class="card-hint">Target: {{ renewableTarget }}%</span>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="overview-card">
              <div class="card-icon purple">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="card-info">
                <span class="card-label">Reduction vs Baseline</span>
                <span class="card-value" :style="{ color: reductionPercentage >= 0 ? '#10b981' : '#ef4444' }">
                  {{ reductionPercentage >= 0 ? '-' : '+' }}{{ Math.abs(reductionPercentage) }}%
                </span>
                <el-progress :percentage="Math.min(100, (reductionPercentage / targetReduction) * 100)" :stroke-width="6" :color="reductionPercentage >= 0 ? '#10b981' : '#ef4444'" :show-text="false" />
                <span class="card-hint">Target: -{{ targetReduction }}%</span>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- Carbon Emissions Breakdown -->
      <div class="emissions-section">
        <el-card class="emissions-card" shadow="hover">
          <div class="card-header">
            <div class="card-title">
              <el-icon><PieChart /></el-icon>
              <span>Carbon Emissions by Scope</span>
            </div>
            <el-radio-group v-model="emissionsTimeframe" size="small">
              <el-radio-button label="monthly">Monthly</el-radio-button>
              <el-radio-button label="quarterly">Quarterly</el-radio-button>
              <el-radio-button label="yearly">Yearly</el-radio-button>
            </el-radio-group>
          </div>
          <div class="emissions-content">
            <div class="emissions-chart">
              <canvas id="scopeEmissionsChart"></canvas>
            </div>
            <div class="emissions-stats">
              <div class="scope-item scope1">
                <div class="scope-header">
                  <span class="scope-color"></span>
                  <span class="scope-name">Scope 1 (Direct)</span>
                  <span class="scope-value">{{ scope1Emissions }} tCO₂e</span>
                </div>
                <div class="scope-details">
                  <span>Generator Fuel: {{ scope1Details.generator }} t</span>
                  <span>Natural Gas: {{ scope1Details.naturalGas }} t</span>
                  <span>Refrigerants: {{ scope1Details.refrigerants }} t</span>
                </div>
              </div>
              <div class="scope-item scope2">
                <div class="scope-header">
                  <span class="scope-color"></span>
                  <span class="scope-name">Scope 2 (Indirect - Electricity)</span>
                  <span class="scope-value">{{ scope2Emissions }} tCO₂e</span>
                </div>
                <div class="scope-details">
                  <span>Grid Electricity: {{ scope2Details.grid }} t</span>
                  <span>Renewable Credits: -{{ scope2Details.renewable }} t</span>
                </div>
              </div>
              <div class="scope-item scope3">
                <div class="scope-header">
                  <span class="scope-color"></span>
                  <span class="scope-name">Scope 3 (Value Chain)</span>
                  <span class="scope-value">{{ scope3Emissions }} tCO₂e</span>
                </div>
                <div class="scope-details">
                  <span>Supply Chain: {{ scope3Details.supplyChain }} t</span>
                  <span>Business Travel: {{ scope3Details.travel }} t</span>
                  <span>Waste: {{ scope3Details.waste }} t</span>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- Carbon Trends -->
      <div class="trends-section">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card class="trend-card" shadow="hover">
              <div class="card-header">
                <div class="card-title">
                  <el-icon><TrendCharts /></el-icon>
                  <span>Carbon Emissions Trend</span>
                </div>
                <el-select v-model="trendPeriod" size="small" style="width: 100px">
                  <el-option label="6 Months" value="6m" />
                  <el-option label="12 Months" value="12m" />
                  <el-option label="24 Months" value="24m" />
                </el-select>
              </div>
              <div class="chart-container">
                <canvas id="carbonTrendChart"></canvas>
              </div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card class="trend-card" shadow="hover">
              <div class="card-header">
                <div class="card-title">
                  <el-icon><DataLine /></el-icon>
                  <span>Carbon Intensity Trend</span>
                </div>
              </div>
              <div class="chart-container">
                <canvas id="intensityTrendChart"></canvas>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Reduction Opportunities -->
      <div class="opportunities-section">
        <div class="section-header">
          <h3>Carbon Reduction Opportunities</h3>
          <el-button type="primary" link @click="viewAllOpportunities">View All →</el-button>
        </div>
        <div class="opportunities-grid">
          <div v-for="opp in reductionOpportunities" :key="opp.id" class="opportunity-card" :class="opp.priority">
            <div class="opp-icon">
              <el-icon><component :is="opp.icon" /></el-icon>
            </div>
            <div class="opp-content">
              <h4>{{ opp.title }}</h4>
              <p>{{ opp.description }}</p>
              <div class="opp-metrics">
                <span class="opp-reduction">Reduction: {{ opp.reduction }} tCO₂e/year</span>
                <span class="opp-savings">Savings: ${{ opp.savings }}/year</span>
                <span class="opp-roi">ROI: {{ opp.roi }} months</span>
              </div>
            </div>
            <div class="opp-action">
              <el-button type="primary" size="small" @click="implementOpportunity(opp)">Implement</el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- Renewable Energy Sources -->
      <div class="renewable-section">
        <el-card class="renewable-card" shadow="hover">
          <div class="card-header">
            <div class="card-title">
              <el-icon><Sunny /></el-icon>
              <span>Renewable Energy Sources</span>
            </div>
            <el-button size="small" @click="addRenewableSource">Add Source</el-button>
          </div>
          <div class="renewable-sources">
            <div v-for="source in renewableSources" :key="source.id" class="source-item">
              <div class="source-icon" :style="{ background: source.color }">
                <el-icon><component :is="source.icon" /></el-icon>
              </div>
              <div class="source-info">
                <div class="source-name">{{ source.name }}</div>
                <div class="source-capacity">Capacity: {{ source.capacity }} MW</div>
              </div>
              <div class="source-production">
                <span class="production-label">Production (YTD)</span>
                <span class="production-value">{{ source.production }} MWh</span>
                <el-progress :percentage="source.percentage" :stroke-width="6" :color="source.color" />
              </div>
              <div class="source-emission">
                <span class="emission-label">Emissions Avoided</span>
                <span class="emission-value">{{ source.emissionsAvoided }} tCO₂e</span>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- Carbon Offset Projects -->
      <div class="offset-section">
        <div class="section-header">
          <h3>Carbon Offset Projects</h3>
          <el-button type="primary" link @click="viewAllProjects">View All →</el-button>
        </div>
        <div class="offset-grid">
          <div v-for="project in offsetProjects" :key="project.id" class="offset-card">
            <div class="offset-header">
              <span class="offset-title">{{ project.name }}</span>
              <el-tag :type="project.status === 'Active' ? 'success' : 'info'" size="small">{{ project.status }}</el-tag>
            </div>
            <div class="offset-details">
              <div class="offset-location">
                <el-icon><Location /></el-icon>
                <span>{{ project.location }}</span>
              </div>
              <div class="offset-type">
                <el-icon><Document /></el-icon>
                <span>{{ project.type }}</span>
              </div>
              <div class="offset-offset">
                <span class="offset-label">Offset Credits:</span>
                <span class="offset-value">{{ project.offsetCredits }} tCO₂e</span>
              </div>
              <div class="offset-cost">
                <span class="offset-label">Cost:</span>
                <span class="offset-value">${{ project.cost }}/t</span>
              </div>
            </div>
            <div class="offset-progress">
              <el-progress :percentage="project.progress" :stroke-width="8" :color="getProgressColor(project.progress)" />
              <span class="progress-text">{{ project.progress }}% Complete</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="action-buttons">
        <el-button type="primary" size="large" @click="generateCarbonReport">
          <el-icon><Document /></el-icon>
          Generate Carbon Report
        </el-button>
        <el-button size="large" @click="scheduleAudit">
          <el-icon><Calendar /></el-icon>
          Schedule Carbon Audit
        </el-button>
        <el-button size="large" @click="viewRecommendations">
          <el-icon><Setting /></el-icon>
          View Recommendations
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  DataLine, TrendCharts, Sunny, PieChart, Cpu, Download, Setting,
  WarningFilled, Document, Calendar, Location, WindPower, Monitor,
  OfficeBuilding, Van, Grid, Key, Tools, MagicStick
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading carbon optimization data...')

// ==================== Reactive Data ====================
const emissionsTimeframe = ref('monthly')
const trendPeriod = ref('12m')
const carbonAlert = ref(true)
const alertSeverity = ref('warning')
const alertMessage = ref('Carbon emissions 8% above target this quarter. Optimization recommended.')

// Carbon metrics
const totalCarbon = ref(12500)
const annualTarget = ref(15000)
const carbonIntensity = ref(285)
const targetIntensity = ref(250)
const renewablePercentage = ref(42)
const renewableTarget = ref(50)
const reductionPercentage = ref(12)
const targetReduction = ref(25)

// Scope emissions
const scope1Emissions = ref(1850)
const scope2Emissions = ref(8750)
const scope3Emissions = ref(1900)

const scope1Details = ref({
  generator: 850,
  naturalGas: 650,
  refrigerants: 350
})

const scope2Details = ref({
  grid: 9850,
  renewable: 1100
})

const scope3Details = ref({
  supplyChain: 1200,
  travel: 450,
  waste: 250
})

// Reduction opportunities
const reductionOpportunities = ref([
  { id: 1, title: 'Increase Renewable Energy Procurement', description: 'Purchase additional renewable energy credits to offset grid electricity', reduction: 1250, savings: 150000, roi: 18, priority: 'high', icon: 'Sunny' },
  { id: 2, title: 'Optimize PUE to 1.35', description: 'Implement cooling optimization and airflow management', reduction: 850, savings: 102000, roi: 12, priority: 'high', icon: 'Cpu' },
  { id: 3, title: 'Replace Generators with BESS', description: 'Install battery energy storage for backup power', reduction: 450, savings: 54000, roi: 24, priority: 'medium', icon: 'Monitor' },
  { id: 4, title: 'Implement Heat Recovery', description: 'Capture waste heat for facility heating', reduction: 320, savings: 38000, roi: 36, priority: 'medium', icon: 'Temperature' }
])

// Renewable sources
const renewableSources = ref([
  { id: 1, name: 'Solar Farm', icon: 'Sunny', color: '#f59e0b', capacity: 15, production: 18500, percentage: 42, emissionsAvoided: 2850 },
  { id: 2, name: 'Wind Power', icon: 'WindPower', color: '#3b82f6', capacity: 10, production: 12500, percentage: 28, emissionsAvoided: 1920 },
  { id: 3, name: 'Hydro Power', icon: 'Drop', color: '#10b981', capacity: 8, production: 9800, percentage: 22, emissionsAvoided: 1510 },
  { id: 4, name: 'Biomass', icon: 'Leaf', color: '#8b5cf6', capacity: 3, production: 3600, percentage: 8, emissionsAvoided: 550 }
])

// Offset projects
const offsetProjects = ref([
  { id: 1, name: 'Amazon Rainforest Conservation', location: 'Brazil', type: 'Forestry', offsetCredits: 2500, cost: 12, progress: 75, status: 'Active' },
  { id: 2, name: 'Wind Farm Development', location: 'India', type: 'Renewable Energy', offsetCredits: 1800, cost: 8, progress: 60, status: 'Active' },
  { id: 3, name: 'Methane Capture Project', location: 'USA', type: 'Waste Management', offsetCredits: 1200, cost: 15, progress: 40, status: 'Active' }
])

// Helper functions
const getProgressColor = (percentage: number) => {
  if (percentage < 50) return '#10b981'
  if (percentage < 75) return '#84cc16'
  if (percentage < 90) return '#f59e0b'
  return '#ef4444'
}

// Chart instances
let scopeEmissionsChart: echarts.ECharts | null = null
let carbonTrendChart: echarts.ECharts | null = null
let intensityTrendChart: echarts.ECharts | null = null

// Chart initialization
const initScopeEmissionsChart = () => {
  const canvas = document.getElementById('scopeEmissionsChart') as HTMLCanvasElement
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

  if (scopeEmissionsChart) scopeEmissionsChart.dispose()
  scopeEmissionsChart = echarts.init(canvas, null, { width: width, height: height, devicePixelRatio: pixelRatio })

  let data: any
  if (emissionsTimeframe.value === 'monthly') {
    data = {
      tooltip: { trigger: 'axis' },
      legend: { data: ['Scope 1', 'Scope 2', 'Scope 3'], bottom: 0, left: 'center' },
      grid: { top: 40, left: 60, right: 40, bottom: 50, containLabel: true },
      xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] },
      yAxis: { type: 'value', name: 'Emissions (tCO₂e)' },
      series: [
        { name: 'Scope 1', type: 'bar', data: [145, 148, 152, 155, 158, 160, 162, 158, 155, 152, 148, 145], itemStyle: { color: '#f59e0b', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top' } },
        { name: 'Scope 2', type: 'bar', data: [680, 690, 710, 730, 740, 750, 760, 745, 725, 710, 695, 680], itemStyle: { color: '#3b82f6', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top' } },
        { name: 'Scope 3', type: 'bar', data: [145, 148, 152, 155, 158, 160, 162, 158, 155, 152, 148, 145], itemStyle: { color: '#10b981', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top' } }
      ]
    }
  } else if (emissionsTimeframe.value === 'quarterly') {
    data = {
      tooltip: { trigger: 'axis' },
      legend: { data: ['Scope 1', 'Scope 2', 'Scope 3'], bottom: 0, left: 'center' },
      grid: { top: 40, left: 60, right: 40, bottom: 50, containLabel: true },
      xAxis: { type: 'category', data: ['Q1', 'Q2', 'Q3', 'Q4'] },
      yAxis: { type: 'value', name: 'Emissions (tCO₂e)' },
      series: [
        { name: 'Scope 1', type: 'bar', data: [445, 468, 475, 445], itemStyle: { color: '#f59e0b', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top' } },
        { name: 'Scope 2', type: 'bar', data: [2080, 2180, 2220, 2080], itemStyle: { color: '#3b82f6', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top' } },
        { name: 'Scope 3', type: 'bar', data: [445, 468, 475, 445], itemStyle: { color: '#10b981', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top' } }
      ]
    }
  } else {
    data = {
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie', radius: ['40%', '70%'], center: ['50%', '50%'],
        data: [
          { value: scope1Emissions.value, name: 'Scope 1', itemStyle: { color: '#f59e0b' } },
          { value: scope2Emissions.value, name: 'Scope 2', itemStyle: { color: '#3b82f6' } },
          { value: scope3Emissions.value, name: 'Scope 3', itemStyle: { color: '#10b981' } }
        ],
        label: { show: true, formatter: '{b}: {d}%' }
      }]
    }
  }
  scopeEmissionsChart.setOption(data)
}

const initCarbonTrendChart = () => {
  const canvas = document.getElementById('carbonTrendChart') as HTMLCanvasElement
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

  if (carbonTrendChart) carbonTrendChart.dispose()
  carbonTrendChart = echarts.init(canvas, null, { width: width, height: height, devicePixelRatio: pixelRatio })

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

  carbonTrendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Actual Emissions', 'Baseline', 'Target'], bottom: 0, left: 'center' },
    grid: { top: 40, left: 60, right: 40, bottom: 50, containLabel: true },
    xAxis: { type: 'category', data: months, axisLabel: { fontSize: 11 } },
    yAxis: { type: 'value', name: 'Emissions (tCO₂e)' },
    series: [
      { name: 'Actual Emissions', type: 'line', data: [980, 1020, 1050, 1080, 1100, 1120, 1150, 1130, 1100, 1070, 1040, 1000], smooth: true, lineStyle: { color: '#ef4444', width: 2 }, areaStyle: { opacity: 0.1 }, symbol: 'circle', symbolSize: 6 },
      { name: 'Baseline', type: 'line', data: [1050, 1050, 1050, 1050, 1050, 1050, 1050, 1050, 1050, 1050, 1050, 1050], lineStyle: { color: '#909399', width: 2, type: 'dashed' } },
      { name: 'Target', type: 'line', data: [1000, 990, 980, 970, 960, 950, 940, 930, 920, 910, 900, 890], lineStyle: { color: '#10b981', width: 2, type: 'dashed' } }
    ]
  })
}

const initIntensityTrendChart = () => {
  const canvas = document.getElementById('intensityTrendChart') as HTMLCanvasElement
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

  if (intensityTrendChart) intensityTrendChart.dispose()
  intensityTrendChart = echarts.init(canvas, null, { width: width, height: height, devicePixelRatio: pixelRatio })

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

  intensityTrendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Carbon Intensity', 'Target'], bottom: 0, left: 'center' },
    grid: { top: 40, left: 60, right: 40, bottom: 50, containLabel: true },
    xAxis: { type: 'category', data: months, axisLabel: { fontSize: 11 } },
    yAxis: { type: 'value', name: 'Intensity (gCO₂e/kWh)' },
    series: [
      { name: 'Carbon Intensity', type: 'line', data: [310, 305, 300, 295, 290, 288, 285, 282, 280, 278, 275, 272], smooth: true, lineStyle: { color: '#3b82f6', width: 2 }, areaStyle: { opacity: 0.1 }, symbol: 'circle', symbolSize: 6 },
      { name: 'Target', type: 'line', data: [300, 295, 290, 285, 280, 275, 270, 265, 260, 255, 250, 250], lineStyle: { color: '#10b981', width: 2, type: 'dashed' } }
    ]
  })
}

// Actions
const runOptimization = () => {
  ElMessage.success('Carbon optimization started. Results will be available shortly.')
}

const exportReport = () => {
  ElMessage.success('Carbon report export started')
}

const setCarbonTargets = () => {
  ElMessage.info('Carbon target configuration interface will open')
}

const viewCarbonDetails = () => {
  ElMessage.info('Viewing carbon emission details')
}

const viewAllOpportunities = () => {
  ElMessage.info('Viewing all reduction opportunities')
}

const implementOpportunity = (opp: any) => {
  ElMessage.success(`Implementing: ${opp.title}`)
}

const addRenewableSource = () => {
  ElMessage.info('Add renewable source interface will open')
}

const viewAllProjects = () => {
  ElMessage.info('Viewing all offset projects')
}

const generateCarbonReport = () => {
  ElMessage.success('Carbon report generation started')
}

const scheduleAudit = () => {
  ElMessage.info('Carbon audit scheduling interface will open')
}

const viewRecommendations = () => {
  ElMessage.info('Viewing AI-powered recommendations')
}

// Window resize handler
let resizeTimer: ReturnType<typeof setTimeout> | null = null
const handleResize = () => {
  if (resizeTimer) clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => {
    if (scopeEmissionsChart) scopeEmissionsChart.resize()
    if (carbonTrendChart) carbonTrendChart.resize()
    if (intensityTrendChart) intensityTrendChart.resize()
  }, 200)
}

// Loading simulation
const startLoading = () => {
  const interval = setInterval(() => {
    if (loadingProgress.value < 90) loadingProgress.value += Math.random() * 10
  }, 200)
  return interval
}

// Watch for timeframe changes
const refreshCharts = () => {
  setTimeout(() => {
    initScopeEmissionsChart()
    initCarbonTrendChart()
    initIntensityTrendChart()
  }, 100)
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
          initScopeEmissionsChart()
          initCarbonTrendChart()
          initIntensityTrendChart()
          window.addEventListener('resize', handleResize)
        }, 200)
      })
    }, 400)
  }, 2800)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (resizeTimer) clearTimeout(resizeTimer)
  if (scopeEmissionsChart) scopeEmissionsChart.dispose()
  if (carbonTrendChart) carbonTrendChart.dispose()
  if (intensityTrendChart) intensityTrendChart.dispose()
})
</script>

<style scoped>
/* ==================== Loading Screen ==================== */
.carbon-optimization-container {
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
.carbon-optimization-main {
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

.alert-banner.critical {
  background: #fef2f2;
  border-left: 4px solid #ef4444;
  color: #dc2626;
}

.alert-banner.warning {
  background: #fffbeb;
  border-left: 4px solid #f59e0b;
  color: #d97706;
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

.card-icon.green { background: #ecfdf5; color: #10b981; }
.card-icon.blue { background: #eff6ff; color: #3b82f6; }
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
  margin-bottom: 8px;
}

.card-hint {
  display: block;
  font-size: 11px;
  color: #94a3b8;
  margin-top: 4px;
}

/* Emissions Section */
.emissions-section {
  margin-bottom: 24px;
}

.emissions-card {
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

.emissions-content {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.emissions-chart {
  flex: 2;
  min-width: 400px;
}

.emissions-stats {
  flex: 1;
  min-width: 250px;
}

.scope-item {
  background: #f8fafc;
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 16px;
}

.scope-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.scope-color {
  width: 12px;
  height: 12px;
  border-radius: 4px;
}

.scope1 .scope-color { background: #f59e0b; }
.scope2 .scope-color { background: #3b82f6; }
.scope3 .scope-color { background: #10b981; }

.scope-name {
  flex: 1;
  font-weight: 600;
  color: #1e293b;
}

.scope-value {
  font-weight: 700;
  color: #1e293b;
}

.scope-details {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 12px;
  color: #64748b;
}

/* Trends Section */
.trends-section {
  margin-bottom: 24px;
}

.trend-card {
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

/* Opportunities Section */
.opportunities-section {
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

.opportunities-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.opportunity-card {
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

.opportunity-card:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.opportunity-card.high {
  border-left-color: #ef4444;
}

.opportunity-card.medium {
  border-left-color: #f59e0b;
}

.opportunity-card.low {
  border-left-color: #10b981;
}

.opp-icon {
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

.opp-content {
  flex: 1;
}

.opp-content h4 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 4px 0;
}

.opp-content p {
  font-size: 13px;
  color: #64748b;
  margin: 0 0 8px 0;
}

.opp-metrics {
  display: flex;
  gap: 16px;
  font-size: 12px;
}

.opp-reduction {
  color: #10b981;
}

.opp-savings {
  color: #f59e0b;
}

.opp-roi {
  color: #3b82f6;
}

.opp-action {
  flex-shrink: 0;
}

/* Renewable Section */
.renewable-section {
  margin-bottom: 24px;
}

.renewable-card {
  border-radius: 20px;
  background: white;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.renewable-sources {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.source-item {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 16px;
  flex-wrap: wrap;
}

.source-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.source-info {
  min-width: 150px;
}

.source-name {
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 4px;
}

.source-capacity {
  font-size: 12px;
  color: #64748b;
}

.source-production {
  flex: 1;
  min-width: 200px;
}

.production-label {
  display: block;
  font-size: 11px;
  color: #64748b;
  margin-bottom: 4px;
}

.production-value {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
}

.source-emission {
  text-align: right;
  min-width: 150px;
}

.emission-label {
  display: block;
  font-size: 11px;
  color: #64748b;
  margin-bottom: 4px;
}

.emission-value {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #10b981;
}

/* Offset Section */
.offset-section {
  margin-bottom: 24px;
}

.offset-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.offset-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
}

.offset-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.offset-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.offset-title {
  font-weight: 600;
  color: #1e293b;
}

.offset-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
  font-size: 13px;
  color: #64748b;
}

.offset-location,
.offset-type {
  display: flex;
  align-items: center;
  gap: 8px;
}

.offset-offset,
.offset-cost {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #e2e8f0;
}

.offset-label {
  color: #64748b;
}

.offset-value {
  font-weight: 600;
  color: #1e293b;
}

.offset-progress {
  margin-top: 12px;
}

.progress-text {
  display: block;
  text-align: center;
  font-size: 11px;
  color: #64748b;
  margin-top: 4px;
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
  .carbon-optimization-main { padding: 16px; }
  .emissions-content { flex-direction: column; }
  .emissions-chart { min-width: auto; }
  .source-item { flex-direction: column; align-items: flex-start; }
  .source-production { width: 100%; }
  .source-emission { text-align: left; width: 100%; }
}

@media (max-width: 768px) {
  .page-header { flex-direction: column; align-items: flex-start; gap: 16px; }
  .opportunity-card { flex-direction: column; }
  .opp-action { align-self: flex-end; }
  .offset-grid { grid-template-columns: 1fr; }
  .action-buttons { flex-direction: column; }
  .action-buttons .el-button { width: 100%; }
}
</style>