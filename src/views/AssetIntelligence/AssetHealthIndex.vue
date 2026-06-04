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
          <span class="loading-title">Asset Health Index</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Asset Health & Performance Intelligence</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="asset-health-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><TrendCharts /></el-icon>
          Asset Health Index
        </h1>
        <div class="page-subtitle">Monitor asset health scores, degradation trends, and risk assessment</div>
      </div>
      <div class="header-actions">
        <el-button @click="exportData">
          <el-icon><Download /></el-icon> Export Report
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
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalAssets }}</div>
          <div class="stat-label">Total Assets</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.healthyAssets }}</div>
          <div class="stat-label">Healthy (≥80)</div>
          <div class="stat-trend up">{{ stats.healthyPercent }}% of total</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.degradingAssets }}</div>
          <div class="stat-label">Degrading (60-79)</div>
          <div class="stat-trend down">{{ stats.degradingPercent }}% of total</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">
          <el-icon><CircleClose /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.criticalAssets }}</div>
          <div class="stat-label">Critical (<60)</div>
          <div class="stat-trend down">{{ stats.criticalPercent }}% of total</div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Row -->
    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-title">Overall Health Score</div>
        <div class="metric-value">{{ metrics.overallHealth }}<span class="metric-unit">/100</span></div>
        <div class="metric-trend" :class="metrics.healthTrend > 0 ? 'positive' : 'negative'">
          {{ metrics.healthTrend > 0 ? '↑' : '↓' }} {{ Math.abs(metrics.healthTrend) }} points vs last month
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Average Degradation Rate</div>
        <div class="metric-value">{{ metrics.avgDegradation }}<span class="metric-unit">%/year</span></div>
        <div class="metric-trend negative">Accelerating</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Assets Requiring Attention</div>
        <div class="metric-value">{{ metrics.attentionAssets }}</div>
        <div class="metric-sub">Health score < 70</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Predicted Failures (12m)</div>
        <div class="metric-value">{{ metrics.predictedFailures }}</div>
        <div class="metric-trend negative">↑ {{ metrics.failureRisk }}% risk increase</div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Health Score Distribution</span>
          <span class="chart-subtitle">Asset health score range</span>
        </div>
        <div class="chart-container" ref="distributionChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Health by Category</span>
          <span class="chart-subtitle">Average health score per category</span>
        </div>
        <div class="chart-container" ref="categoryChartEl"></div>
      </div>
    </div>

    <!-- Second Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Health Trend (Last 12 Months)</span>
          <span class="chart-subtitle">Overall health index trend</span>
        </div>
        <div class="chart-container" ref="trendChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Risk Matrix</span>
          <span class="chart-subtitle">Criticality vs Health Score</span>
        </div>
        <div class="chart-container" ref="riskMatrixChartEl"></div>
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
        <el-select v-model="healthFilter" placeholder="Health Status" clearable style="width: 140px">
          <el-option label="Healthy (≥80)" value="healthy" />
          <el-option label="Degrading (60-79)" value="degrading" />
          <el-option label="Critical (<60)" value="critical" />
        </el-select>
        <el-select v-model="locationFilter" placeholder="Location" clearable filterable style="width: 150px">
          <el-option v-for="l in uniqueLocations" :key="l" :label="l" :value="l" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button type="primary" link @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon> Reset Filters
        </el-button>
      </div>
    </div>

    <!-- Assets Health Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">Asset Health Details</span>
        <el-button size="small" @click="viewAllAssets">View All →</el-button>
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
        <el-table-column prop="healthScore" label="Health Score" width="160">
          <template #default="{ row }">
            <el-progress
                :percentage="row.healthScore"
                :stroke-width="10"
                :color="getHealthColor(row.healthScore)"
                :format="(p: number) => `${p}%`"
            />
          </template>
        </el-table-column>
        <el-table-column prop="degradationRate" label="Degradation" width="110">
          <template #default="{ row }">
            <span :class="row.degradationRate > 15 ? 'metric-bad' : (row.degradationRate > 8 ? 'metric-warning' : 'metric-good')">
              {{ row.degradationRate }}%/yr
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="remainingLife" label="Remaining Life" width="120">
          <template #default="{ row }">
            <span :class="row.remainingLife < 2 ? 'metric-bad' : (row.remainingLife < 5 ? 'metric-warning' : 'metric-good')">
              {{ row.remainingLife }} years
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="riskLevel" label="Risk Level" width="110">
          <template #default="{ row }">
            <el-tag :type="getRiskTagType(row.riskLevel)" size="small">{{ row.riskLevel }}</el-tag>
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
            <div class="detail-stat-value" :style="{ color: getHealthColor(selectedAsset.healthScore) }">
              {{ selectedAsset.healthScore }}%
            </div>
            <div class="detail-stat-label">Health Score</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedAsset.degradationRate }}%/yr</div>
            <div class="detail-stat-label">Degradation Rate</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedAsset.remainingLife }} yrs</div>
            <div class="detail-stat-label">Remaining Life</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedAsset.failureProbability }}%</div>
            <div class="detail-stat-label">Failure Probability</div>
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
          <el-descriptions-item label="Risk Level">
            <el-tag :type="getRiskTagType(selectedAsset.riskLevel)" size="small">{{ selectedAsset.riskLevel }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Last Assessment">{{ selectedAsset.lastAssessment }}</el-descriptions-item>
        </el-descriptions>

        <!-- Health Trend Chart -->
        <div class="detail-section">
          <div class="section-title">Health Degradation Trend</div>
          <div class="trend-chart" ref="assetTrendChartEl"></div>
        </div>

        <!-- Health Factors -->
        <div class="detail-section">
          <div class="section-title">Health Impact Factors</div>
          <el-table :data="selectedAsset.healthFactors" border stripe>
            <el-table-column prop="factor" label="Factor" width="200" />
            <el-table-column prop="score" label="Score" width="120">
              <template #default="{ row }">
                <el-progress :percentage="row.score" :stroke-width="8" :color="getHealthColor(row.score)" />
              </template>
            </el-table-column>
            <el-table-column prop="weight" label="Weight" width="100" />
            <el-table-column prop="status" label="Status" width="120">
              <template #default="{ row }">
                <el-tag :type="row.score >= 80 ? 'success' : (row.score >= 60 ? 'warning' : 'danger')" size="small">
                  {{ row.score >= 80 ? 'Good' : (row.score >= 60 ? 'Warning' : 'Critical') }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="recommendation" label="Recommendation" min-width="200" />
          </el-table>
        </div>

        <!-- Recommendations -->
        <div class="detail-section" v-if="selectedAsset.recommendations">
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
        <el-button type="primary" @click="generateReport(selectedAsset)">Generate Report</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  TrendCharts, Plus, Download, Refresh, CircleCheck, Warning, CircleClose,
  Search, RefreshLeft
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading asset health data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading asset health data...',
  'Calculating health scores...',
  'Analyzing degradation trends...',
  'Assessing risk levels...',
  'Almost ready...'
]

// ==================== Types ====================
interface HealthFactor {
  factor: string
  score: number
  weight: string
  status: string
  recommendation: string
}

interface HealthTrend {
  date: string
  score: number
}

interface Recommendation {
  title: string
  type: 'warning' | 'error' | 'info' | 'success'
  description: string
}

interface AssetHealth {
  id: number
  tag: string
  name: string
  category: string
  manufacturer: string
  model: string
  location: string
  healthScore: number
  degradationRate: number
  remainingLife: number
  failureProbability: number
  riskLevel: string
  installDate: string
  lastAssessment: string
  healthTrend: HealthTrend[]
  healthFactors: HealthFactor[]
  recommendations?: Recommendation
}

// ==================== Mock Data (65 assets) ====================
const generateAssetHealthData = (): AssetHealth[] => {
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
  const riskLevels = ['Critical', 'High', 'Medium', 'Low']

  const assets: AssetHealth[] = []

  for (let i = 1; i <= 65; i++) {
    const category = categories[Math.floor(Math.random() * categories.length)]
    const manufacturerList = manufacturers[category as keyof typeof manufacturers] || ['Generic']
    const manufacturer = manufacturerList[Math.floor(Math.random() * manufacturerList.length)]

    const installDate = new Date()
    installDate.setMonth(installDate.getMonth() - Math.random() * 120)
    const installDateStr = installDate.toISOString().slice(0, 10)

    const ageYears = (new Date().getTime() - installDate.getTime()) / (1000 * 60 * 60 * 24 * 365)

    // Calculate health score based on age and random factors
    let baseHealth = 100 - ageYears * 6 + (Math.random() * 15 - 7.5)
    baseHealth = Math.max(35, Math.min(98, baseHealth))
    const healthScore = Math.round(baseHealth)

    // Degradation rate (% per year)
    const degradationRate = parseFloat((5 + Math.random() * 15 + (ageYears * 0.5)).toFixed(1))

    // Remaining life (years)
    let remainingLife = 0
    if (healthScore >= 80) remainingLife = parseFloat((5 + Math.random() * 5).toFixed(1))
    else if (healthScore >= 60) remainingLife = parseFloat((2 + Math.random() * 3).toFixed(1))
    else remainingLife = parseFloat((0.5 + Math.random() * 1.5).toFixed(1))

    // Failure probability (%)
    const failureProbability = Math.min(95, Math.max(5, Math.round(100 - healthScore + (Math.random() * 10 - 5))))

    // Risk level
    let riskLevel = ''
    if (healthScore >= 80 && failureProbability < 20) riskLevel = 'Low'
    else if (healthScore >= 60 && failureProbability < 40) riskLevel = 'Medium'
    else if (healthScore >= 40) riskLevel = 'High'
    else riskLevel = 'Critical'

    // Generate health trend (last 12 months)
    const healthTrend: HealthTrend[] = []
    for (let m = 11; m >= 0; m--) {
      const date = new Date()
      date.setMonth(date.getMonth() - m)
      let trendScore = healthScore + (Math.random() * 8 - 4) + (m * 0.3)
      trendScore = Math.max(30, Math.min(100, trendScore))
      healthTrend.push({
        date: date.toISOString().slice(0, 7),
        score: Math.round(trendScore)
      })
    }

    // Generate health factors
    const healthFactors: HealthFactor[] = [
      {
        factor: 'Age',
        score: Math.max(30, Math.min(100, 100 - ageYears * 5 + (Math.random() * 10 - 5))),
        weight: '25%',
        status: '',
        recommendation: ageYears > 8 ? 'Consider replacement planning' : 'Monitor regularly'
      },
      {
        factor: 'Maintenance History',
        score: 60 + Math.random() * 35,
        weight: '20%',
        status: '',
        recommendation: Math.random() > 0.7 ? 'Increase preventive maintenance frequency' : 'Maintenance schedule adequate'
      },
      {
        factor: 'Operational Efficiency',
        score: 50 + Math.random() * 45,
        weight: '20%',
        status: '',
        recommendation: 'Optimize operating parameters'
      },
      {
        factor: 'Failure Rate',
        score: Math.max(40, 100 - Math.random() * 40),
        weight: '15%',
        status: '',
        recommendation: 'Monitor failure patterns'
      },
      {
        factor: 'Environmental Conditions',
        score: 60 + Math.random() * 35,
        weight: '10%',
        status: '',
        recommendation: 'Check environmental controls'
      },
      {
        factor: 'Spare Parts Availability',
        score: 50 + Math.random() * 45,
        weight: '10%',
        status: '',
        recommendation: 'Ensure critical spares in stock'
      }
    ]

    // Update factor status based on score
    healthFactors.forEach(f => {
      if (f.score >= 80) f.status = 'Good'
      else if (f.score >= 60) f.status = 'Warning'
      else f.status = 'Critical'
    })

    // Generate recommendations
    let recommendations: Recommendation | undefined
    if (healthScore < 55) {
      recommendations = {
        title: 'Urgent Action Required',
        type: 'error',
        description: `Asset health is critically low (${healthScore}%). Immediate maintenance or replacement recommended.`
      }
    } else if (healthScore < 70) {
      recommendations = {
        title: 'Maintenance Recommended',
        type: 'warning',
        description: `Asset health is below optimal level (${healthScore}%). Schedule comprehensive maintenance within 90 days.`
      }
    } else if (degradationRate > 15) {
      recommendations = {
        title: 'Degradation Alert',
        type: 'warning',
        description: `High degradation rate detected (${degradationRate}%/year). Investigate root cause.`
      }
    }

    assets.push({
      id: i,
      tag: `${category.substring(0, 3).toUpperCase()}-${String(i).padStart(4, '0')}`,
      name: `${category} ${String.fromCharCode(64 + Math.ceil(i / 8))}${((i - 1) % 8) + 1}`,
      category: category,
      manufacturer: manufacturer,
      model: `${category}-${Math.floor(Math.random() * 1000)}`,
      location: locations[Math.floor(Math.random() * locations.length)],
      healthScore: healthScore,
      degradationRate: degradationRate,
      remainingLife: remainingLife,
      failureProbability: failureProbability,
      riskLevel: riskLevel,
      installDate: installDateStr,
      lastAssessment: new Date().toISOString().slice(0, 10),
      healthTrend: healthTrend,
      healthFactors: healthFactors,
      recommendations: recommendations
    })
  }

  return assets
}

const assets = ref<AssetHealth[]>(generateAssetHealthData())

// ==================== State ====================
const searchText = ref('')
const categoryFilter = ref('')
const healthFilter = ref('')
const locationFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)
const selectedAsset = ref<AssetHealth | null>(null)

// Chart refs
let distributionChart: echarts.ECharts | null = null
let categoryChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null
let riskMatrixChart: echarts.ECharts | null = null
let assetTrendChart: echarts.ECharts | null = null

const distributionChartEl = ref<HTMLElement | null>(null)
const categoryChartEl = ref<HTMLElement | null>(null)
const trendChartEl = ref<HTMLElement | null>(null)
const riskMatrixChartEl = ref<HTMLElement | null>(null)
const assetTrendChartEl = ref<HTMLElement | null>(null)

// ==================== Computed ====================
const stats = computed(() => {
  const totalAssets = assets.value.length
  const healthyAssets = assets.value.filter(a => a.healthScore >= 80).length
  const degradingAssets = assets.value.filter(a => a.healthScore >= 60 && a.healthScore < 80).length
  const criticalAssets = assets.value.filter(a => a.healthScore < 60).length

  return {
    totalAssets,
    healthyAssets,
    degradingAssets,
    criticalAssets,
    healthyPercent: Math.round((healthyAssets / totalAssets) * 100),
    degradingPercent: Math.round((degradingAssets / totalAssets) * 100),
    criticalPercent: Math.round((criticalAssets / totalAssets) * 100)
  }
})

const metrics = computed(() => {
  const overallHealth = Math.round(assets.value.reduce((sum, a) => sum + a.healthScore, 0) / assets.value.length)
  const avgDegradation = (assets.value.reduce((sum, a) => sum + a.degradationRate, 0) / assets.value.length).toFixed(1)
  const attentionAssets = assets.value.filter(a => a.healthScore < 70).length
  const predictedFailures = assets.value.filter(a => a.failureProbability > 70).length
  const failureRisk = 12.5

  return {
    overallHealth,
    healthTrend: -2.5,
    avgDegradation: parseFloat(avgDegradation),
    attentionAssets,
    predictedFailures,
    failureRisk
  }
})

const uniqueCategories = computed(() => {
  return [...new Set(assets.value.map(a => a.category))]
})

const uniqueLocations = computed(() => {
  return [...new Set(assets.value.map(a => a.location))]
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

  if (healthFilter.value) {
    if (healthFilter.value === 'healthy') filtered = filtered.filter(a => a.healthScore >= 80)
    else if (healthFilter.value === 'degrading') filtered = filtered.filter(a => a.healthScore >= 60 && a.healthScore < 80)
    else if (healthFilter.value === 'critical') filtered = filtered.filter(a => a.healthScore < 60)
  }

  if (locationFilter.value) {
    filtered = filtered.filter(a => a.location === locationFilter.value)
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

const getRiskTagType = (risk: string): string => {
  const map: Record<string, string> = { Critical: 'danger', High: 'warning', Medium: 'info', Low: 'success' }
  return map[risk] || 'info'
}

const resetFilters = () => {
  searchText.value = ''
  categoryFilter.value = ''
  healthFilter.value = ''
  locationFilter.value = ''
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

// ==================== Chart Functions ====================
const initDistributionChart = () => {
  if (!distributionChartEl.value) return
  if (distributionChart) {
    distributionChart.dispose()
    distributionChart = null
  }

  const ranges = ['90-100', '80-89', '70-79', '60-69', '50-59', '<50']
  const counts = [0, 0, 0, 0, 0, 0]

  assets.value.forEach(a => {
    if (a.healthScore >= 90) counts[0]++
    else if (a.healthScore >= 80) counts[1]++
    else if (a.healthScore >= 70) counts[2]++
    else if (a.healthScore >= 60) counts[3]++
    else if (a.healthScore >= 50) counts[4]++
    else counts[5]++
  })

  distributionChart = echarts.init(distributionChartEl.value)
  distributionChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: ranges },
    yAxis: { type: 'value', name: 'Number of Assets' },
    series: [{
      type: 'bar',
      data: counts,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const idx = params.dataIndex
          if (idx <= 1) return '#22c55e'
          if (idx <= 3) return '#f59e0b'
          return '#ef4444'
        }
      },
      label: { show: true, position: 'top' }
    }]
  })
}

const initCategoryChart = () => {
  if (!categoryChartEl.value) return
  if (categoryChart) {
    categoryChart.dispose()
    categoryChart = null
  }

  const categoryMap = new Map<string, { total: number; count: number }>()
  assets.value.forEach(a => {
    const existing = categoryMap.get(a.category) || { total: 0, count: 0 }
    existing.total += a.healthScore
    existing.count++
    categoryMap.set(a.category, existing)
  })

  const data = Array.from(categoryMap.entries())
      .map(([name, { total, count }]) => ({ name, value: Math.round(total / count) }))
      .sort((a, b) => b.value - a.value)

  categoryChart = echarts.init(categoryChartEl.value)
  categoryChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: '{b}<br/>Avg Health Score: {c}%' },
    grid: { top: 30, left: 50, right: 20, bottom: 40, containLabel: true },
    xAxis: { type: 'category', data: data.map(d => d.name), axisLabel: { rotate: 30, fontSize: 11 } },
    yAxis: { type: 'value', name: 'Health Score (%)', min: 40, max: 100 },
    series: [{
      type: 'bar',
      data: data.map(d => d.value),
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const value = params.value
          if (value >= 80) return '#22c55e'
          if (value >= 60) return '#f59e0b'
          return '#ef4444'
        }
      },
      label: { show: true, position: 'top', formatter: '{c}%' }
    }]
  })
}

const initTrendChart = () => {
  if (!trendChartEl.value) return
  if (trendChart) {
    trendChart.dispose()
    trendChart = null
  }

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  // Calculate average health score for each month
  const monthlyAverages = [85, 84, 83, 82, 81, 80, 79, 78, 77, 76, 75, 74]

  trendChart = echarts.init(trendChartEl.value)
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'Health Score (%)', min: 60, max: 100 },
    series: [{
      type: 'line',
      data: monthlyAverages,
      smooth: true,
      lineStyle: { color: '#3b82f6', width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      areaStyle: { opacity: 0.1, color: '#3b82f6' },
      label: { show: true, position: 'top', formatter: '{c}%' }
    }]
  })
}

const initRiskMatrixChart = () => {
  if (!riskMatrixChartEl.value) return
  if (riskMatrixChart) {
    riskMatrixChart.dispose()
    riskMatrixChart = null
  }

  // Prepare data for scatter plot: [healthScore, failureProbability, category]
  const data = assets.value.map(a => ({
    value: [a.healthScore, a.failureProbability],
    name: a.name,
    category: a.category
  }))

  riskMatrixChart = echarts.init(riskMatrixChartEl.value)
  riskMatrixChart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        const health = params.value[0]
        const probability = params.value[1]
        return `${params.name}<br/>Health Score: ${health}%<br/>Failure Probability: ${probability}%`
      }
    },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'value', name: 'Health Score (%)', min: 30, max: 100 },
    yAxis: { type: 'value', name: 'Failure Probability (%)', min: 0, max: 100 },
    series: [{
      type: 'scatter',
      data: data,
      symbolSize: 12,
      itemStyle: {
        color: (params: any) => {
          const health = params.value[0]
          if (health >= 80) return '#22c55e'
          if (health >= 60) return '#f59e0b'
          return '#ef4444'
        }
      },
      label: { show: false }
    }]
  })
}

const initAssetTrendChart = () => {
  if (!assetTrendChartEl.value || !selectedAsset.value) return
  if (assetTrendChart) {
    assetTrendChart.dispose()
    assetTrendChart = null
  }

  const months = selectedAsset.value.healthTrend.map(t => t.date)
  const scores = selectedAsset.value.healthTrend.map(t => t.score)

  assetTrendChart = echarts.init(assetTrendChartEl.value)
  assetTrendChart.setOption({
    tooltip: { trigger: 'axis', formatter: '{b}<br/>Health Score: {c}%' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: months, axisLabel: { rotate: 30, fontSize: 11 } },
    yAxis: { type: 'value', name: 'Health Score (%)', min: 30, max: 100 },
    series: [{
      type: 'line',
      data: scores,
      smooth: true,
      lineStyle: { color: '#3b82f6', width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      areaStyle: { opacity: 0.1 },
      label: { show: true, position: 'top', formatter: '{c}%' }
    }]
  })
}

const refreshCharts = () => {
  nextTick(() => {
    initDistributionChart()
    initCategoryChart()
    initTrendChart()
    initRiskMatrixChart()
  })
}

// ==================== Actions ====================
const viewAssetDetail = (asset: AssetHealth) => {
  selectedAsset.value = asset
  detailDialogVisible.value = true
  nextTick(() => initAssetTrendChart())
}

const viewAllAssets = () => {
  ElMessage.info('Viewing all assets')
}

const exportData = () => {
  ElMessage.success('Exporting asset health data...')
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

const generateReport = (asset: AssetHealth | null) => {
  if (!asset) return
  ElMessage.success(`Generating health report for ${asset.name}...`)
  setTimeout(() => {
    ElMessage.success('Report generated successfully')
  }, 1500)
}

// 窗口缩放处理
let resizeTimer: ReturnType<typeof setTimeout> | null = null
const handleResize = () => {
  if (resizeTimer) clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => {
    const charts = [distributionChart, categoryChart, trendChart, riskMatrixChart, assetTrendChart]
    charts.forEach(chart => {
      if (chart && !chart.isDisposed()) chart.resize()
    })
  }, 100)
}

// ==================== Watch ====================
watch([searchText, categoryFilter, healthFilter, locationFilter], () => {
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
  const charts = [distributionChart, categoryChart, trendChart, riskMatrixChart, assetTrendChart]
  charts.forEach(chart => {
    if (chart && !chart.isDisposed()) chart.dispose()
  })
})
</script>

<style scoped>
.asset-health-page {
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
.stat-icon.green { background: #dcfce7; color: #22c55e; }
.stat-icon.orange { background: #fef3c7; color: #f59e0b; }
.stat-icon.red { background: #fee2e2; color: #ef4444; }

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

.stat-trend.up { color: #22c55e; }
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
  font-size: 32px;
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

.detail-stat-sub {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 2px;
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