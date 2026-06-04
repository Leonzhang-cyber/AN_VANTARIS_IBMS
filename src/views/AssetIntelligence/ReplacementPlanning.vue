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
          <span class="loading-title">Replacement Planning</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Asset Replacement & Capital Planning</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="replacement-planning-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Calendar /></el-icon>
          Replacement Planning
        </h1>
        <div class="page-subtitle">Plan and optimize asset replacement schedules and CAPEX budgeting</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="generatePlan">
          <el-icon><Document /></el-icon> Generate Plan
        </el-button>
        <el-button @click="exportData">
          <el-icon><Download /></el-icon> Export
        </el-button>
        <el-button @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon> Refresh
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue">
          <el-icon><Calendar /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalAssets }}</div>
          <div class="stat-label">Total Assets</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.dueForReplacement }}</div>
          <div class="stat-label">Due for Replacement</div>
          <div class="stat-trend up">Next 12 months</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">
          <el-icon><CircleClose /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.overdueReplacement }}</div>
          <div class="stat-label">Overdue</div>
          <div class="stat-trend down">Requires immediate action</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><Coin /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">${{ stats.totalBudget.toLocaleString() }}</div>
          <div class="stat-label">Total Budget Required</div>
          <div class="stat-trend up">Next 5 years</div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Row -->
    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-title">Average Replacement Cost</div>
        <div class="metric-value">${{ metrics.avgReplacementCost.toLocaleString() }}</div>
        <div class="metric-sub">Per asset</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Annual Budget Forecast</div>
        <div class="metric-value">${{ metrics.annualBudget.toLocaleString() }}</div>
        <div class="metric-trend" :class="metrics.budgetTrend > 0 ? 'positive' : 'negative'">
          {{ metrics.budgetTrend > 0 ? '↑' : '↓' }} {{ Math.abs(metrics.budgetTrend) }}% vs last year
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-title">ROI on Replacements</div>
        <div class="metric-value">{{ metrics.roi }}<span class="metric-unit">%</span></div>
        <div class="metric-trend positive">Energy savings +{{ metrics.energySavings }}%</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Payback Period</div>
        <div class="metric-value">{{ metrics.paybackPeriod }}<span class="metric-unit">years</span></div>
        <div class="metric-sub">Average across assets</div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Replacement Forecast (5 Years)</span>
          <span class="chart-subtitle">Assets to be replaced by year</span>
        </div>
        <div class="chart-container" ref="forecastChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Budget Allocation by Category</span>
          <span class="chart-subtitle">CAPEX distribution</span>
        </div>
        <div class="chart-container" ref="budgetChartEl"></div>
      </div>
    </div>

    <!-- Second Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Replacement Priority by Category</span>
          <span class="chart-subtitle">Urgency levels across asset types</span>
        </div>
        <div class="chart-container" ref="priorityChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Cost vs Benefit Analysis</span>
          <span class="chart-subtitle">Replacement cost vs expected savings</span>
        </div>
        <div class="chart-container" ref="costBenefitChartEl"></div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-input
            v-model="searchText"
            placeholder="Search by asset name or tag..."
            style="width: 220px"
            clearable
            :prefix-icon="Search"
        />
        <el-select v-model="categoryFilter" placeholder="Category" clearable style="width: 140px">
          <el-option v-for="c in uniqueCategories" :key="c" :label="c" :value="c" />
        </el-select>
        <el-select v-model="priorityFilter" placeholder="Priority" clearable style="width: 130px">
          <el-option label="Critical" value="Critical" />
          <el-option label="High" value="High" />
          <el-option label="Medium" value="Medium" />
          <el-option label="Low" value="Low" />
        </el-select>
        <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 140px">
          <el-option label="Due Now" value="due" />
          <el-option label="Planned" value="planned" />
          <el-option label="Future" value="future" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button type="primary" link @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon> Reset Filters
        </el-button>
      </div>
    </div>

    <!-- Replacement Plan Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">Replacement Schedule</span>
        <el-button size="small" @click="viewAllPlan">View All →</el-button>
      </div>
      <el-table :data="paginatedAssets" stripe style="width: 100%" v-loading="tableLoading"
                @row-click="viewAssetDetail">
        <el-table-column prop="tag" label="Asset Tag" width="120" />
        <el-table-column prop="name" label="Asset Name" min-width="180" />
        <el-table-column prop="category" label="Category" width="120">
          <template #default="{ row }">
            <el-tag :type="getCategoryTagType(row.category)" size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="location" label="Location" width="150" />
        <el-table-column prop="currentHealth" label="Health" width="140">
          <template #default="{ row }">
            <el-progress :percentage="row.currentHealth" :stroke-width="8" :color="getHealthColor(row.currentHealth)" />
          </template>
        </el-table-column>
        <el-table-column prop="replacementYear" label="Replacement Year" width="130">
          <template #default="{ row }">
            <el-tag :type="getYearTagType(row.replacementYear)" size="small">{{ row.replacementYear }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="estimatedCost" label="Est. Cost" width="120">
          <template #default="{ row }">
            ${{ row.estimatedCost.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="Priority" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityTagType(row.priority)" size="small">{{ row.priority }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="roi" label="ROI" width="80">
          <template #default="{ row }">
            <span :class="row.roi > 15 ? 'metric-good' : (row.roi > 8 ? 'metric-warning' : 'metric-bad')">
              {{ row.roi }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click.stop="viewAssetDetail(row)">Details</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="totalRecords"
            layout="total, sizes, prev, pager, next"
            background
        />
      </div>
    </div>

    <!-- Asset Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="selectedAsset?.name" width="900px" class="asset-dialog">
      <div v-if="selectedAsset" class="asset-detail">
        <!-- Header Stats -->
        <div class="detail-header-stats">
          <div class="detail-stat">
            <div class="detail-stat-value" :style="{ color: getHealthColor(selectedAsset.currentHealth) }">
              {{ selectedAsset.currentHealth }}%
            </div>
            <div class="detail-stat-label">Current Health</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedAsset.predictedHealthAtReplacement }}%</div>
            <div class="detail-stat-label">Predicted Health at Replacement</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">${{ selectedAsset.estimatedCost.toLocaleString() }}</div>
            <div class="detail-stat-label">Estimated Cost</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedAsset.roi }}%</div>
            <div class="detail-stat-label">Expected ROI</div>
          </div>
        </div>

        <!-- Basic Info -->
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Asset Tag">{{ selectedAsset.tag }}</el-descriptions-item>
          <el-descriptions-item label="Category">{{ selectedAsset.category }}</el-descriptions-item>
          <el-descriptions-item label="Manufacturer">{{ selectedAsset.manufacturer }}</el-descriptions-item>
          <el-descriptions-item label="Model">{{ selectedAsset.model }}</el-descriptions-item>
          <el-descriptions-item label="Location">{{ selectedAsset.location }}</el-descriptions-item>
          <el-descriptions-item label="Install Date">{{ selectedAsset.installDate }}</el-descriptions-item>
          <el-descriptions-item label="Current Age">{{ selectedAsset.currentAge }} years</el-descriptions-item>
          <el-descriptions-item label="Expected Lifespan">{{ selectedAsset.expectedLifespan }} years</el-descriptions-item>
          <el-descriptions-item label="Replacement Year">{{ selectedAsset.replacementYear }}</el-descriptions-item>
          <el-descriptions-item label="Priority">
            <el-tag :type="getPriorityTagType(selectedAsset.priority)" size="small">{{ selectedAsset.priority }}</el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <!-- Health Forecast Chart -->
        <div class="detail-section">
          <div class="section-title">Health Degradation Forecast</div>
          <div class="trend-chart" ref="forecastDetailChartEl"></div>
        </div>

        <!-- Financial Analysis -->
        <div class="detail-section">
          <div class="section-title">Financial Analysis</div>
          <el-table :data="selectedAsset.financialAnalysis" border stripe>
            <el-table-column prop="item" label="Item" width="200" />
            <el-table-column prop="cost" label="Cost" width="150">
              <template #default="{ row }">
                ${{ row.cost.toLocaleString() }}
              </template>
            </el-table-column>
            <el-table-column prop="savings" label="Annual Savings" width="150">
              <template #default="{ row }">
                ${{ row.savings.toLocaleString() }}
              </template>
            </el-table-column>
            <el-table-column prop="payback" label="Payback Period" width="120" />
            <el-table-column prop="notes" label="Notes" min-width="200" />
          </el-table>
        </div>

        <!-- Recommendations -->
        <div class="detail-section">
          <div class="section-title">Recommendations</div>
          <el-alert
              :title="selectedAsset.recommendations.title"
              :type="selectedAsset.recommendations.type"
              :description="selectedAsset.recommendations.description"
              :closable="false"
              show-icon
          />
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="approveReplacement(selectedAsset)">Approve Replacement</el-button>
        <el-button type="warning" @click="postponeReplacement(selectedAsset)">Postpone</el-button>
      </template>
    </el-dialog>

    <!-- Generate Plan Dialog -->
    <el-dialog v-model="planDialogVisible" title="Generate Replacement Plan" width="500px">
      <el-form :model="planForm" label-width="140px">
        <el-form-item label="Planning Horizon">
          <el-select v-model="planForm.horizon" style="width: 100%">
            <el-option label="1 Year" value="1" />
            <el-option label="3 Years" value="3" />
            <el-option label="5 Years" value="5" />
            <el-option label="10 Years" value="10" />
          </el-select>
        </el-form-item>
        <el-form-item label="Budget Constraint">
          <el-input-number v-model="planForm.budget" :min="0" :step="100000" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Optimization Goal">
          <el-select v-model="planForm.goal" style="width: 100%">
            <el-option label="Minimize Risk" value="risk" />
            <el-option label="Maximize ROI" value="roi" />
            <el-option label="Balance Budget" value="budget" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="planDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="savePlan">Generate Plan</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Calendar, Plus, Download, Refresh, CircleCheck, Warning, CircleClose,
  Search, RefreshLeft, Document, Coin
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading replacement planning data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading asset data...',
  'Analyzing replacement schedules...',
  'Calculating budget forecasts...',
  'Optimizing replacement plan...',
  'Almost ready...'
]

// ==================== Types ====================
interface FinancialItem {
  item: string
  cost: number
  savings: number
  payback: string
  notes: string
}

interface Recommendation {
  title: string
  type: 'warning' | 'error' | 'info' | 'success'
  description: string
}

interface ReplacementAsset {
  id: number
  tag: string
  name: string
  category: string
  manufacturer: string
  model: string
  location: string
  currentHealth: number
  predictedHealthAtReplacement: number
  currentAge: number
  expectedLifespan: number
  replacementYear: string
  estimatedCost: number
  priority: string
  roi: number
  energySavings: number
  installDate: string
  healthForecast: { year: number; health: number }[]
  financialAnalysis: FinancialItem[]
  recommendations: Recommendation
}

// ==================== Mock Data (70 assets for replacement planning) ====================
const generateReplacementData = (): ReplacementAsset[] => {
  const categories = ['UPS', 'Generator', 'CRAC', 'Chiller', 'Switchgear', 'Server', 'Storage', 'Network']
  const manufacturers = {
    'UPS': ['Schneider Electric', 'Eaton', 'Vertiv', 'ABB'],
    'Generator': ['Caterpillar', 'Cummins', 'MTU', 'Kohler'],
    'CRAC': ['Stulz', 'Vertiv', 'Schneider Electric', 'Daikin'],
    'Chiller': ['Trane', 'Carrier', 'York', 'Daikin'],
    'Switchgear': ['ABB', 'Siemens', 'Schneider Electric', 'Eaton'],
    'Server': ['Dell', 'HP', 'Cisco', 'Lenovo'],
    'Storage': ['Dell EMC', 'NetApp', 'Pure Storage', 'HPE'],
    'Network': ['Cisco', 'Juniper', 'Arista', 'Huawei']
  }
  const locations = ['Data Center A', 'Data Center B', 'Server Room 1', 'Server Room 2', 'Generator Room', 'UPS Room', 'Chiller Plant']
  const priorities = ['Critical', 'High', 'Medium', 'Low']

  const currentYear = new Date().getFullYear()
  const assets: ReplacementAsset[] = []

  for (let i = 1; i <= 70; i++) {
    const category = categories[Math.floor(Math.random() * categories.length)]
    const manufacturerList = manufacturers[category as keyof typeof manufacturers] || ['Generic']
    const manufacturer = manufacturerList[Math.floor(Math.random() * manufacturerList.length)]

    const installDate = new Date()
    const ageYears = 2 + Math.random() * 13
    installDate.setFullYear(currentYear - Math.floor(ageYears))
    const installDateStr = installDate.toISOString().slice(0, 10)

    const expectedLifespan = category === 'Server' ? 5 : (category === 'Storage' ? 6 : (category === 'Network' ? 7 : 12))
    const currentAge = parseFloat(ageYears.toFixed(1))
    const remainingLife = Math.max(0, expectedLifespan - currentAge)

    // Calculate health score
    let healthScore = 100 - (currentAge / expectedLifespan) * 40 + (Math.random() * 10 - 5)
    healthScore = Math.max(35, Math.min(98, healthScore))

    // Determine replacement year
    let replacementYear = ''
    let priority = ''
    if (remainingLife <= 1) {
      replacementYear = currentYear.toString()
      priority = 'Critical'
    } else if (remainingLife <= 2) {
      replacementYear = (currentYear + 1).toString()
      priority = 'High'
    } else if (remainingLife <= 4) {
      replacementYear = (currentYear + Math.floor(remainingLife)).toString()
      priority = 'Medium'
    } else {
      replacementYear = (currentYear + Math.floor(remainingLife)).toString()
      priority = 'Low'
    }

    // Estimated cost based on category
    const baseCost = {
      'UPS': 25000, 'Generator': 75000, 'CRAC': 35000, 'Chiller': 80000,
      'Switchgear': 45000, 'Server': 15000, 'Storage': 30000, 'Network': 20000
    }
    const cost = (baseCost[category as keyof typeof baseCost] || 20000) * (0.7 + Math.random() * 0.6)
    const estimatedCost = Math.round(cost / 1000) * 1000

    // Calculate ROI
    const energySavings = category === 'CRAC' || category === 'Chiller' ? 15 + Math.random() * 15 : 5 + Math.random() * 10
    const roi = parseFloat((energySavings + (remainingLife < 2 ? 20 : 5)).toFixed(1))

    // Generate health forecast
    const healthForecast = []
    for (let y = 0; y <= Math.min(5, Math.ceil(remainingLife) + 2); y++) {
      let forecastHealth = healthScore - (y / expectedLifespan) * 40
      forecastHealth = Math.max(20, Math.min(100, forecastHealth))
      healthForecast.push({
        year: currentYear + y,
        health: Math.round(forecastHealth)
      })
    }

    // Generate financial analysis
    const financialAnalysis: FinancialItem[] = [
      {
        item: 'New Equipment Cost',
        cost: estimatedCost,
        savings: 0,
        payback: '-',
        notes: 'Purchase and installation'
      },
      {
        item: 'Energy Savings (Annual)',
        cost: 0,
        savings: Math.round(estimatedCost * (energySavings / 100) * 0.3),
        payback: `${(estimatedCost / (estimatedCost * (energySavings / 100) * 0.3)).toFixed(1)} years`,
        notes: `Estimated ${energySavings}% reduction in energy consumption`
      },
      {
        item: 'Maintenance Reduction',
        cost: 0,
        savings: Math.round(estimatedCost * 0.08),
        payback: 'Immediate',
        notes: 'Reduced maintenance costs with new equipment'
      },
      {
        item: 'Downtime Risk Reduction',
        cost: 0,
        savings: Math.round(estimatedCost * 0.12),
        payback: 'Immediate',
        notes: 'Lower risk of unplanned outages'
      }
    ]

    // Generate recommendations
    let recommendations: Recommendation
    if (remainingLife <= 1) {
      recommendations = {
        title: 'Immediate Replacement Required',
        type: 'error',
        description: `Asset has reached end of life (${currentAge}/${expectedLifespan} years). Schedule replacement immediately to avoid failure.`
      }
    } else if (remainingLife <= 2.5) {
      recommendations = {
        title: 'Plan Replacement Within 12 Months',
        type: 'warning',
        description: `Asset health is declining rapidly. Expected ROI of ${roi}% makes replacement financially beneficial.`
      }
    } else {
      recommendations = {
        title: 'Monitor and Plan Ahead',
        type: 'info',
        description: `Asset has ${remainingLife.toFixed(1)} years of expected life remaining. Start budget planning for ${replacementYear}.`
      }
    }

    assets.push({
      id: i,
      tag: `${category.substring(0, 3).toUpperCase()}-${String(i).padStart(4, '0')}`,
      name: `${category} ${String.fromCharCode(64 + Math.ceil(i / 7))}${((i - 1) % 7) + 1}`,
      category: category,
      manufacturer: manufacturer,
      model: `${category}-${Math.floor(Math.random() * 1000)}`,
      location: locations[Math.floor(Math.random() * locations.length)],
      currentHealth: Math.round(healthScore),
      predictedHealthAtReplacement: Math.max(20, Math.round(healthScore - (remainingLife / expectedLifespan) * 40)),
      currentAge: currentAge,
      expectedLifespan: expectedLifespan,
      replacementYear: replacementYear,
      estimatedCost: estimatedCost,
      priority: priority,
      roi: roi,
      energySavings: energySavings,
      installDate: installDateStr,
      healthForecast: healthForecast,
      financialAnalysis: financialAnalysis,
      recommendations: recommendations
    })
  }

  return assets
}

const assets = ref<ReplacementAsset[]>(generateReplacementData())

// ==================== State ====================
const searchText = ref('')
const categoryFilter = ref('')
const priorityFilter = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)
const planDialogVisible = ref(false)
const selectedAsset = ref<ReplacementAsset | null>(null)

// Chart refs
let forecastChart: echarts.ECharts | null = null
let budgetChart: echarts.ECharts | null = null
let priorityChart: echarts.ECharts | null = null
let costBenefitChart: echarts.ECharts | null = null
let forecastDetailChart: echarts.ECharts | null = null

const forecastChartEl = ref<HTMLElement | null>(null)
const budgetChartEl = ref<HTMLElement | null>(null)
const priorityChartEl = ref<HTMLElement | null>(null)
const costBenefitChartEl = ref<HTMLElement | null>(null)
const forecastDetailChartEl = ref<HTMLElement | null>(null)

const planForm = ref({
  horizon: '5',
  budget: 500000,
  goal: 'balanced'
})

// ==================== Computed ====================
const stats = computed(() => {
  const totalAssets = assets.value.length
  const dueForReplacement = assets.value.filter(a => a.replacementYear === new Date().getFullYear().toString() || a.replacementYear === (new Date().getFullYear() + 1).toString()).length
  const overdueReplacement = assets.value.filter(a => parseInt(a.replacementYear) < new Date().getFullYear()).length
  const totalBudget = assets.value.reduce((sum, a) => sum + a.estimatedCost, 0)

  return {
    totalAssets,
    dueForReplacement,
    overdueReplacement,
    totalBudget: Math.round(totalBudget / 1000) * 1000
  }
})

const metrics = computed(() => {
  const totalCost = assets.value.reduce((sum, a) => sum + a.estimatedCost, 0)
  const avgReplacementCost = totalCost / assets.value.length
  const thisYearCost = assets.value.filter(a => a.replacementYear === new Date().getFullYear().toString())
      .reduce((sum, a) => sum + a.estimatedCost, 0)
  const avgRoi = assets.value.reduce((sum, a) => sum + a.roi, 0) / assets.value.length
  const avgEnergySavings = assets.value.reduce((sum, a) => sum + a.energySavings, 0) / assets.value.length
  const avgPayback = (avgReplacementCost / (avgReplacementCost * (avgEnergySavings / 100) * 0.3)).toFixed(1)

  return {
    avgReplacementCost: Math.round(avgReplacementCost),
    annualBudget: Math.round(thisYearCost),
    budgetTrend: 8.5,
    roi: parseFloat(avgRoi.toFixed(1)),
    energySavings: parseFloat(avgEnergySavings.toFixed(1)),
    paybackPeriod: parseFloat(avgPayback)
  }
})

const uniqueCategories = computed(() => {
  return [...new Set(assets.value.map(a => a.category))]
})

const filteredAssets = computed(() => {
  let filtered = [...assets.value]

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(a =>
        a.name.toLowerCase().includes(search) ||
        a.tag.toLowerCase().includes(search) ||
        a.location.toLowerCase().includes(search)
    )
  }

  if (categoryFilter.value) {
    filtered = filtered.filter(a => a.category === categoryFilter.value)
  }

  if (priorityFilter.value) {
    filtered = filtered.filter(a => a.priority === priorityFilter.value)
  }

  if (statusFilter.value) {
    const currentYear = new Date().getFullYear()
    if (statusFilter.value === 'due') {
      filtered = filtered.filter(a => parseInt(a.replacementYear) <= currentYear + 1)
    } else if (statusFilter.value === 'planned') {
      filtered = filtered.filter(a => parseInt(a.replacementYear) > currentYear + 1 && parseInt(a.replacementYear) <= currentYear + 3)
    } else if (statusFilter.value === 'future') {
      filtered = filtered.filter(a => parseInt(a.replacementYear) > currentYear + 3)
    }
  }

  return filtered
})

const totalRecords = computed(() => filteredAssets.value.length)

const paginatedAssets = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredAssets.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getHealthColor = (health: number): string => {
  if (health >= 80) return '#22c55e'
  if (health >= 60) return '#f59e0b'
  return '#ef4444'
}

const getCategoryTagType = (category: string): string => {
  const map: Record<string, string> = {
    'UPS': 'primary', 'Generator': 'warning', 'CRAC': 'info', 'Chiller': 'danger',
    'Switchgear': 'success', 'Server': '', 'Storage': '', 'Network': ''
  }
  return map[category] || 'info'
}

const getPriorityTagType = (priority: string): string => {
  const map: Record<string, string> = { Critical: 'danger', High: 'warning', Medium: 'info', Low: 'success' }
  return map[priority] || 'info'
}

const getYearTagType = (year: string): string => {
  const currentYear = new Date().getFullYear()
  const yearNum = parseInt(year)
  if (yearNum <= currentYear) return 'danger'
  if (yearNum <= currentYear + 1) return 'warning'
  return 'info'
}

const resetFilters = () => {
  searchText.value = ''
  categoryFilter.value = ''
  priorityFilter.value = ''
  statusFilter.value = ''
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

// ==================== Chart Functions ====================
const initForecastChart = () => {
  if (!forecastChartEl.value) return
  if (forecastChart) {
    forecastChart.dispose()
    forecastChart = null
  }

  const currentYear = new Date().getFullYear()
  const years = [currentYear, currentYear + 1, currentYear + 2, currentYear + 3, currentYear + 4]
  const counts = years.map(y => assets.value.filter(a => parseInt(a.replacementYear) === y).length)
  const costs = years.map(y => assets.value.filter(a => parseInt(a.replacementYear) === y).reduce((sum, a) => sum + a.estimatedCost, 0) / 1000)

  forecastChart = echarts.init(forecastChartEl.value)
  forecastChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Number of Assets', 'Total Cost (K$)'], bottom: 0 },
    grid: { top: 40, left: 60, right: 60, bottom: 40 },
    xAxis: { type: 'category', data: years },
    yAxis: [
      { type: 'value', name: 'Number of Assets', position: 'left' },
      { type: 'value', name: 'Cost (K$)', position: 'right' }
    ],
    series: [
      { name: 'Number of Assets', type: 'bar', data: counts, itemStyle: { color: '#3b82f6', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top' } },
      { name: 'Total Cost (K$)', type: 'line', data: costs, lineStyle: { color: '#ef4444', width: 3 }, symbol: 'circle', symbolSize: 8, label: { show: true, position: 'top', formatter: '${c}K' } }
    ]
  })
}

const initBudgetChart = () => {
  if (!budgetChartEl.value) return
  if (budgetChart) {
    budgetChart.dispose()
    budgetChart = null
  }

  const categoryMap = new Map<string, number>()
  assets.value.forEach(a => {
    categoryMap.set(a.category, (categoryMap.get(a.category) || 0) + a.estimatedCost)
  })

  const data = Array.from(categoryMap.entries())
      .sort((a, b) => b[1] - a[1])
      .map(([name, value]) => ({ name, value: Math.round(value / 1000) }))

  budgetChart = echarts.init(budgetChartEl.value)
  budgetChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}<br/>Budget: ${c}K' },
    legend: { orient: 'vertical', left: 'left', data: data.map(d => d.name) },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: data,
      label: { show: true, formatter: '{b}: ${c}K' },
      emphasis: { scale: true }
    }]
  })
}

const initPriorityChart = () => {
  if (!priorityChartEl.value) return
  if (priorityChart) {
    priorityChart.dispose()
    priorityChart = null
  }

  const categoryMap = new Map<string, { critical: number; high: number; medium: number; low: number }>()

  assets.value.forEach(a => {
    const existing = categoryMap.get(a.category) || { critical: 0, high: 0, medium: 0, low: 0 }
    if (a.priority === 'Critical') existing.critical++
    else if (a.priority === 'High') existing.high++
    else if (a.priority === 'Medium') existing.medium++
    else existing.low++
    categoryMap.set(a.category, existing)
  })

  const categories = Array.from(categoryMap.keys())
  const criticalData = categories.map(c => categoryMap.get(c)?.critical || 0)
  const highData = categories.map(c => categoryMap.get(c)?.high || 0)
  const mediumData = categories.map(c => categoryMap.get(c)?.medium || 0)
  const lowData = categories.map(c => categoryMap.get(c)?.low || 0)

  priorityChart = echarts.init(priorityChartEl.value)
  priorityChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['Critical', 'High', 'Medium', 'Low'], bottom: 0 },
    grid: { top: 30, left: 50, right: 20, bottom: 40, containLabel: true },
    xAxis: { type: 'category', data: categories, axisLabel: { rotate: 30, fontSize: 11 } },
    yAxis: { type: 'value', name: 'Number of Assets' },
    series: [
      { name: 'Critical', type: 'bar', stack: 'total', data: criticalData, itemStyle: { color: '#ef4444' }, label: { show: true, position: 'inside' } },
      { name: 'High', type: 'bar', stack: 'total', data: highData, itemStyle: { color: '#f59e0b' }, label: { show: true, position: 'inside' } },
      { name: 'Medium', type: 'bar', stack: 'total', data: mediumData, itemStyle: { color: '#3b82f6' }, label: { show: true, position: 'inside' } },
      { name: 'Low', type: 'bar', stack: 'total', data: lowData, itemStyle: { color: '#22c55e' }, label: { show: true, position: 'inside' } }
    ]
  })
}

const initCostBenefitChart = () => {
  if (!costBenefitChartEl.value) return
  if (costBenefitChart) {
    costBenefitChart.dispose()
    costBenefitChart = null
  }

  const topAssets = assets.value.filter(a => a.priority === 'Critical' || a.priority === 'High').slice(0, 8)
  const names = topAssets.map(a => a.name.length > 12 ? a.name.slice(0, 12) + '...' : a.name)
  const costs = topAssets.map(a => a.estimatedCost / 1000)
  const rois = topAssets.map(a => a.roi)

  costBenefitChart = echarts.init(costBenefitChartEl.value)
  costBenefitChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Cost (K$)', 'ROI (%)'], bottom: 0 },
    grid: { top: 40, left: 60, right: 60, bottom: 40 },
    xAxis: { type: 'category', data: names, axisLabel: { rotate: 30, fontSize: 10 } },
    yAxis: [
      { type: 'value', name: 'Cost (K$)', position: 'left' },
      { type: 'value', name: 'ROI (%)', position: 'right', min: 0, max: 50 }
    ],
    series: [
      { name: 'Cost (K$)', type: 'bar', data: costs, itemStyle: { color: '#3b82f6', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top', formatter: '${c}K' } },
      { name: 'ROI (%)', type: 'line', data: rois, lineStyle: { color: '#22c55e', width: 3 }, symbol: 'circle', symbolSize: 8, label: { show: true, position: 'top', formatter: '{c}%' } }
    ]
  })
}

const initForecastDetailChart = () => {
  if (!forecastDetailChartEl.value || !selectedAsset.value) return
  if (forecastDetailChart) {
    forecastDetailChart.dispose()
    forecastDetailChart = null
  }

  const years = selectedAsset.value.healthForecast.map(f => f.year)
  const healthData = selectedAsset.value.healthForecast.map(f => f.health)

  forecastDetailChart = echarts.init(forecastDetailChartEl.value)
  forecastDetailChart.setOption({
    tooltip: { trigger: 'axis', formatter: '{b}<br/>Health Score: {c}%' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: years },
    yAxis: { type: 'value', name: 'Health Score (%)', min: 20, max: 100 },
    series: [{
      type: 'line',
      data: healthData,
      smooth: true,
      lineStyle: { color: '#ef4444', width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      areaStyle: { opacity: 0.1, color: '#ef4444' },
      label: { show: true, position: 'top', formatter: '{c}%' }
    }]
  })
}

const refreshCharts = () => {
  nextTick(() => {
    initForecastChart()
    initBudgetChart()
    initPriorityChart()
    initCostBenefitChart()
  })
}

// ==================== Actions ====================
const viewAssetDetail = (asset: ReplacementAsset) => {
  selectedAsset.value = asset
  detailDialogVisible.value = true
  nextTick(() => initForecastDetailChart())
}

const viewAllPlan = () => {
  ElMessage.info('Viewing all replacement plans')
}

const approveReplacement = (asset: ReplacementAsset | null) => {
  if (asset) {
    ElMessage.success(`Replacement approved for ${asset.name}`)
  }
}

const postponeReplacement = (asset: ReplacementAsset | null) => {
  if (asset) {
    ElMessage.warning(`Replacement postponed for ${asset.name}`)
  }
}

const generatePlan = () => {
  planDialogVisible.value = true
}

const savePlan = () => {
  ElMessage.success(`Replacement plan generated for ${planForm.value.horizon} years with budget $${planForm.value.budget.toLocaleString()}`)
  planDialogVisible.value = false
}

const exportData = () => {
  ElMessage.success('Exporting replacement plan data...')
  setTimeout(() => {
    ElMessage.success('Data exported successfully')
  }, 1000)
}

const refreshData = async () => {
  refreshing.value = true
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  refreshing.value = false
  tableLoading.value = false
  refreshCharts()
  ElMessage.success('Data refreshed')
}

// 窗口缩放处理
let resizeTimer: ReturnType<typeof setTimeout> | null = null
const handleResize = () => {
  if (resizeTimer) clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => {
    const charts = [forecastChart, budgetChart, priorityChart, costBenefitChart, forecastDetailChart]
    charts.forEach(chart => {
      if (chart && !chart.isDisposed()) chart.resize()
    })
  }, 100)
}

// ==================== Watch ====================
watch([searchText, categoryFilter, priorityFilter, statusFilter], () => {
  currentPage.value = 1
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
      nextTick(() => refreshCharts())
    }, 500)
  }, 2200)
}

onMounted(() => {
  startLoading()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (resizeTimer) clearTimeout(resizeTimer)
  window.removeEventListener('resize', handleResize)
  const charts = [forecastChart, budgetChart, priorityChart, costBenefitChart, forecastDetailChart]
  charts.forEach(chart => {
    if (chart && !chart.isDisposed()) chart.dispose()
  })
})
</script>

<style scoped>
.replacement-planning-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 24px;
}

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
.spinner-ring:nth-child(4) { border-left-color: #ec489a; animation-delay: 0.6s; width: 20%; height: 20%; top: 40%; left: 40%; }

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

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
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

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.blue { background: #eef2ff; color: #3b82f6; }
.stat-icon.orange { background: #fef3c7; color: #f59e0b; }
.stat-icon.red { background: #fee2e2; color: #ef4444; }
.stat-icon.green { background: #dcfce7; color: #22c55e; }

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  margin-top: 4px;
}

.stat-trend {
  font-size: 11px;
  margin-top: 4px;
}

.stat-trend.up { color: #f59e0b; }
.stat-trend.down { color: #ef4444; }

/* Metrics Row */
.metrics-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.metric-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.metric-title {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.metric-unit {
  font-size: 14px;
  font-weight: normal;
  color: #64748b;
}

.metric-trend {
  font-size: 12px;
  margin: 8px 0 4px;
}

.metric-trend.positive { color: #22c55e; }
.metric-trend.negative { color: #ef4444; }

.metric-sub {
  font-size: 11px;
  color: #64748b;
  margin-top: 4px;
}

/* Charts Row */
.charts-row {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  flex: 1;
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.chart-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
}

.chart-subtitle {
  font-size: 12px;
  color: #64748b;
}

.chart-container {
  height: 280px;
  width: 100%;
}

/* Filter Bar */
.filter-bar {
  background: white;
  border-radius: 16px;
  padding: 14px 20px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.filter-left {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* Table Container */
.table-container {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.table-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

/* Asset Detail */
.asset-detail {
  padding: 8px;
}

.detail-header-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 16px;
}

.detail-stat {
  text-align: center;
}

.detail-stat-value {
  font-size: 24px;
  font-weight: 700;
}

.detail-stat-label {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
}

.detail-section {
  margin-bottom: 24px;
}

.section-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
  margin-bottom: 16px;
  padding-left: 10px;
  border-left: 3px solid #3b82f6;
}

.trend-chart {
  height: 280px;
  width: 100%;
}

.metric-good { color: #22c55e; font-weight: 600; }
.metric-warning { color: #f59e0b; font-weight: 600; }
.metric-bad { color: #ef4444; font-weight: 600; }

/* Responsive */
@media (max-width: 1000px) {
  .stats-grid, .metrics-row {
    grid-template-columns: repeat(2, 1fr);
  }
  .charts-row {
    flex-direction: column;
  }
  .detail-header-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-grid, .metrics-row {
    grid-template-columns: 1fr;
  }
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .filter-left {
    flex-direction: column;
    width: 100%;
  }
  .filter-left .el-input,
  .filter-left .el-select {
    width: 100% !important;
  }
}

/* Element Plus Overrides */
:deep(.el-table) {
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
}
:deep(.el-table th.el-table__cell) {
  background-color: #f8fafc !important;
  color: #334155;
}
:deep(.el-table .el-table__row:hover > td.el-table__cell) {
  background-color: #f0f7ff;
}
:deep(.el-button--primary) {
  background: #3b82f6;
  border-color: #3b82f6;
}
:deep(.el-button--primary:hover) {
  background: #2563eb;
}
:deep(.el-pagination.is-background .el-pager li.is-active) {
  background-color: #3b82f6;
}
:deep(.el-dialog__body) {
  max-height: 600px;
  overflow-y: auto;
}
:deep(.el-progress-bar__inner) {
  border-radius: 4px;
}
</style>