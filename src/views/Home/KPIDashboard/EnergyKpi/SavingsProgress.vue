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
        <div class="loading-tip">Not Developed Yet</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Savings Progress Page Content -->
  <div v-else class="savings-progress-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h1>Savings Progress</h1>
        <p class="subtitle">Track energy savings, cost reduction, and sustainability goal achievement</p>
      </div>
      <div class="header-actions">
        <el-button :icon="Refresh" @click="refreshData">Refresh</el-button>
        <el-button type="primary" :icon="Download" @click="exportReport">Export Report</el-button>
        <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="to"
            start-placeholder="Start Date"
            end-placeholder="End Date"
            :shortcuts="dateShortcuts"
            size="default"
            style="width: 260px"
            @change="handleDateChange"
        />
      </div>
    </div>

    <!-- KPI Summary Cards -->
    <div class="kpi-cards">
      <div class="kpi-card total-savings">
        <div class="kpi-icon">
          <el-icon :size="32"><Money /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">${{ totalSavings }}<span class="unit">k</span></div>
          <div class="kpi-label">Total Cost Savings</div>
        </div>
        <div class="kpi-trend positive">
          <el-icon><CaretTop /></el-icon>
          {{ savingsGrowth }}%
        </div>
      </div>
      <div class="kpi-card energy-saved">
        <div class="kpi-icon">
          <el-icon :size="32"><Lightning /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ formatNumber(energySaved) }}<span class="unit"> kWh</span></div>
          <div class="kpi-label">Energy Saved</div>
        </div>
        <div class="kpi-sub">Equivalent to {{ co2Reduction }} tons CO₂</div>
      </div>
      <div class="kpi-card progress">
        <div class="kpi-icon">
          <el-icon :size="32"><TrendCharts /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ annualProgress }}%</div>
          <div class="kpi-label">Annual Target Progress</div>
        </div>
        <el-progress :percentage="annualProgress" :color="getProgressColor(annualProgress)" :stroke-width="8" style="margin-top: 8px" />
      </div>
      <div class="kpi-card roi">
        <div class="kpi-icon">
          <el-icon :size="32"><Medal /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ roi }}%</div>
          <div class="kpi-label">ROI (YTD)</div>
        </div>
        <div class="kpi-sub">{{ paybackPeriod }} avg payback</div>
      </div>
    </div>

    <!-- Savings Trend Chart -->
    <div class="chart-card">
      <div class="card-header">
        <h3>Savings Trend</h3>
        <el-radio-group v-model="trendPeriod" size="small" @change="fetchTrendData">
          <el-radio-button label="month">Monthly</el-radio-button>
          <el-radio-button label="quarter">Quarterly</el-radio-button>
          <el-radio-button label="year">Yearly</el-radio-button>
        </el-radio-group>
      </div>
      <div class="chart-container" ref="trendChartRef"></div>
    </div>

    <!-- Savings by Initiative and Category -->
    <div class="two-columns">
      <div class="chart-card">
        <div class="card-header">
          <h3>Savings by Initiative</h3>
          <el-select v-model="initiativeFilter" placeholder="Filter by status" clearable size="small" style="width: 130px">
            <el-option label="All" value="all" />
            <el-option label="Completed" value="completed" />
            <el-option label="In Progress" value="in-progress" />
            <el-option label="Planned" value="planned" />
          </el-select>
        </div>
        <div class="chart-container" ref="initiativeChartRef"></div>
      </div>
      <div class="chart-card">
        <div class="card-header">
          <h3>Savings by Category</h3>
        </div>
        <div class="chart-container" ref="categoryChartRef"></div>
      </div>
    </div>

    <!-- Energy Savings Initiatives Table -->
    <div class="table-card">
      <div class="card-header">
        <h3>Energy Savings Initiatives</h3>
        <el-input
            v-model="searchText"
            placeholder="Search initiatives..."
            :prefix-icon="Search"
            style="width: 240px"
            clearable
        />
      </div>
      <el-table :data="paginatedInitiatives" stripe v-loading="tableLoading" style="width: 100%">
        <el-table-column prop="name" label="Initiative" min-width="200" show-overflow-tooltip />
        <el-table-column prop="category" label="Category" width="140">
          <template #default="{ row }">
            <el-tag size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="startDate" label="Start Date" width="110" sortable />
        <el-table-column prop="targetSavings" label="Target (kWh)" width="130" align="right" sortable>
          <template #default="{ row }">
            {{ formatNumber(row.targetSavings) }}
          </template>
        </el-table-column>
        <el-table-column prop="actualSavings" label="Actual (kWh)" width="130" align="right" sortable>
          <template #default="{ row }">
            <span :class="getSavingsClass(row.actualSavings, row.targetSavings)">
              {{ formatNumber(row.actualSavings) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="Progress" width="180">
          <template #default="{ row }">
            <div class="progress-cell">
              <span class="progress-percent">{{ row.progress || 0 }}%</span>
              <el-progress :percentage="row.progress || 0" :color="getProgressColor(row.progress || 0)" :stroke-width="6" :show-text="false" style="flex: 1" />
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="costSavings" label="Cost Savings" width="130" align="right">
          <template #default="{ row }">
            ${{ formatNumber(row.costSavings) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small" effect="dark">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredInitiatives.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Top Performing Initiatives -->
    <div class="top-initiatives-section">
      <div class="section-header">
        <h2>
          <el-icon><Trophy /></el-icon>
          Top Performing Initiatives
        </h2>
        <el-button link type="primary" @click="viewAllInitiatives">View All Initiatives →</el-button>
      </div>
      <div class="initiatives-grid">
        <div v-for="initiative in topInitiatives" :key="initiative.id" class="initiative-card">
          <div class="card-rank" :class="getRankClass(initiative.rank)">
            #{{ initiative.rank }}
          </div>
          <div class="card-content">
            <div class="initiative-name">{{ initiative.name }}</div>
            <div class="initiative-category">{{ initiative.category }}</div>
            <div class="initiative-stats">
              <div class="stat">
                <span class="stat-label">Savings</span>
                <span class="stat-value">{{ formatNumber(initiative.savings) }} kWh</span>
              </div>
              <div class="stat">
                <span class="stat-label">Cost Saved</span>
                <span class="stat-value">${{ formatNumber(initiative.costSaved) }}</span>
              </div>
              <div class="stat">
                <span class="stat-label">Payback</span>
                <span class="stat-value">{{ initiative.payback }}</span>
              </div>
            </div>
            <el-progress :percentage="initiative.progress" :color="getProgressColor(initiative.progress)" :stroke-width="6" />
          </div>
        </div>
      </div>
    </div>

    <!-- Recommendations for Additional Savings -->
    <div class="recommendations-section">
      <div class="section-header">
        <h2>
          <el-icon><EditPen /></el-icon>
          Recommended Opportunities
        </h2>
        <el-button link type="primary" @click="viewAllRecommendations">View All →</el-button>
      </div>
      <div class="recommendations-list">
        <div v-for="rec in recommendations" :key="rec.id" class="recommendation-item">
          <div class="rec-icon" :class="rec.priority">
            <el-icon><Check /></el-icon>
          </div>
          <div class="rec-content">
            <div class="rec-title">{{ rec.title }}</div>
            <div class="rec-description">{{ rec.description }}</div>
            <div class="rec-metrics">
              <span><el-icon><Lightning /></el-icon> Potential Savings: {{ formatNumber(rec.potentialSavings) }} kWh/year</span>
              <span><el-icon><Money /></el-icon> Est. Cost Savings: ${{ formatNumber(rec.estCostSavings) }}/year</span>
              <span><el-icon><Timer /></el-icon> Est. Payback: {{ rec.estPayback }}</span>
            </div>
          </div>
          <div class="rec-actions">
            <el-button size="small" type="primary" plain @click="viewRecommendation(rec)">Details</el-button>
            <el-button size="small" type="success" plain @click="acceptRecommendation(rec)">Accept</el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  Refresh,
  Download,
  Money,
  Lightning,
  TrendCharts,
  Medal,
  Search,
  Trophy,
  EditPen,
  Check,
  Timer,
  CaretTop,
  CaretBottom
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const tableLoading = ref(false)

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing...',
  'Almost ready...'
]

// ==================== Data Structures ====================
interface SavingsInitiative {
  id: number
  name: string
  category: string
  startDate: string
  targetSavings: number
  actualSavings: number
  progress: number
  costSavings: number
  status: 'completed' | 'in-progress' | 'planned' | 'delayed'
  rank?: number
  payback?: string
  savings?: number
  costSaved?: number
}

interface Recommendation {
  id: number
  title: string
  description: string
  priority: 'high' | 'medium' | 'low'
  potentialSavings: number
  estCostSavings: number
  estPayback: string
}

// ==================== State ====================
const dateRange = ref<[Date, Date] | null>(null)
const trendPeriod = ref<'month' | 'quarter' | 'year'>('month')
const initiativeFilter = ref('all')
const searchText = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

// Chart refs
const trendChartRef = ref<HTMLElement | null>(null)
const initiativeChartRef = ref<HTMLElement | null>(null)
const categoryChartRef = ref<HTMLElement | null>(null)
let trendChart: echarts.ECharts | null = null
let initiativeChart: echarts.ECharts | null = null
let categoryChart: echarts.ECharts | null = null

// ==================== Mock Data ====================
const initiatives = ref<SavingsInitiative[]>([
  { id: 1, name: 'LED Lighting Retrofit - Building A', category: 'Lighting', startDate: '2024-01-15', targetSavings: 125000, actualSavings: 132000, progress: 106, costSavings: 19800, status: 'completed', payback: '1.8 years', savings: 132000, costSaved: 19800 },
  { id: 2, name: 'HVAC Chiller Upgrade', category: 'HVAC', startDate: '2024-02-01', targetSavings: 280000, actualSavings: 265000, progress: 95, costSavings: 39750, status: 'in-progress', payback: '3.2 years', savings: 265000, costSaved: 39750 },
  { id: 3, name: 'VFD Installation on Pumps', category: 'HVAC', startDate: '2024-03-10', targetSavings: 85000, actualSavings: 89000, progress: 105, costSavings: 13350, status: 'completed', payback: '2.1 years', savings: 89000, costSaved: 13350 },
  { id: 4, name: 'Solar Panel Installation', category: 'Renewable', startDate: '2024-04-01', targetSavings: 180000, actualSavings: 145000, progress: 81, costSavings: 21750, status: 'in-progress', payback: '5.5 years', savings: 145000, costSaved: 21750 },
  { id: 5, name: 'Occupancy Sensors - Building B', category: 'Lighting', startDate: '2024-05-15', targetSavings: 45000, actualSavings: 52000, progress: 116, costSavings: 7800, status: 'completed', payback: '1.2 years', savings: 52000, costSaved: 7800 },
  { id: 6, name: 'BMS Optimization', category: 'Controls', startDate: '2024-06-01', targetSavings: 95000, actualSavings: 88000, progress: 93, costSavings: 13200, status: 'in-progress', payback: '1.5 years', savings: 88000, costSaved: 13200 },
  { id: 7, name: 'Air Handler Schedule Optimization', category: 'HVAC', startDate: '2024-07-10', targetSavings: 55000, actualSavings: 61000, progress: 111, costSavings: 9150, status: 'completed', payback: '0.8 years', savings: 61000, costSaved: 9150 },
  { id: 8, name: 'Data Center Cooling Efficiency', category: 'DCIM', startDate: '2024-08-01', targetSavings: 220000, actualSavings: 185000, progress: 84, costSavings: 27750, status: 'in-progress', payback: '4.2 years', savings: 185000, costSaved: 27750 },
  { id: 9, name: 'Window Film Installation', category: 'Building Envelope', startDate: '2024-09-15', targetSavings: 35000, actualSavings: 28000, progress: 80, costSavings: 4200, status: 'in-progress', payback: '2.5 years', savings: 28000, costSaved: 4200 },
  { id: 10, name: 'EV Charging Station Optimization', category: 'EV', startDate: '2024-10-01', targetSavings: 25000, actualSavings: 0, progress: 0, costSavings: 0, status: 'planned', payback: '3.0 years', savings: 0, costSaved: 0 }
])

const recommendations = ref<Recommendation[]>([
  { id: 1, title: 'AHU Retro-commissioning', description: 'Re-commission AHU systems to optimize airflow and reduce fan energy consumption.', priority: 'high', potentialSavings: 68000, estCostSavings: 10200, estPayback: '1.2 years' },
  { id: 2, title: 'Chilled Water Reset Strategy', description: 'Implement dynamic chilled water temperature reset based on outdoor conditions.', priority: 'high', potentialSavings: 45000, estCostSavings: 6750, estPayback: '0.5 years' },
  { id: 3, title: 'Rooftop Solar Expansion', description: 'Expand existing solar array by 50 kW capacity for additional renewable generation.', priority: 'medium', potentialSavings: 75000, estCostSavings: 11250, estPayback: '6.0 years' },
  { id: 4, title: 'Smart Plug Load Control', description: 'Install smart plugs to automatically power down office equipment after hours.', priority: 'medium', potentialSavings: 28000, estCostSavings: 4200, estPayback: '1.5 years' }
])

// ==================== Helper Functions ====================
const formatNumber = (value: number): string => {
  if (value === undefined || value === null) return '0'
  return value.toLocaleString()
}

// ==================== Computed Values ====================
const totalSavings = computed(() => {
  const total = initiatives.value.reduce((sum, i) => sum + (i.costSavings || 0), 0)
  return (total / 1000).toFixed(1)
})

const energySaved = computed(() => {
  return initiatives.value.reduce((sum, i) => sum + (i.actualSavings || 0), 0)
})

const co2Reduction = computed(() => {
  const saved = initiatives.value.reduce((sum, i) => sum + (i.actualSavings || 0), 0)
  return Math.round(saved * 0.0004)
})

const annualProgress = computed(() => {
  const target = initiatives.value.filter(i => i.status !== 'planned').reduce((sum, i) => sum + (i.targetSavings || 0), 0)
  const actual = initiatives.value.filter(i => i.status !== 'planned').reduce((sum, i) => sum + (i.actualSavings || 0), 0)
  if (target === 0) return 0
  return Math.round((actual / target) * 100)
})

const roi = computed(() => {
  const totalCost = 450000
  const totalSavingsVal = initiatives.value.reduce((sum, i) => sum + (i.costSavings || 0), 0)
  if (totalCost === 0) return 0
  return Math.round((totalSavingsVal / totalCost) * 100)
})

const paybackPeriod = computed(() => '2.8 years')
const savingsGrowth = computed(() => 12.5)

const topInitiatives = computed(() => {
  return [...initiatives.value]
      .filter(i => i.status !== 'planned' && i.actualSavings > 0)
      .sort((a, b) => (b.actualSavings || 0) - (a.actualSavings || 0))
      .slice(0, 4)
      .map((item, index) => ({
        ...item,
        rank: index + 1,
        savings: item.actualSavings,
        costSaved: item.costSavings,
        progress: item.progress || 0
      }))
})

const filteredInitiatives = computed(() => {
  let result = [...initiatives.value]
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    result = result.filter(i => i.name.toLowerCase().includes(search))
  }
  if (initiativeFilter.value !== 'all') {
    result = result.filter(i => i.status === initiativeFilter.value)
  }
  if (dateRange.value && dateRange.value[0] && dateRange.value[1]) {
    const [start, end] = dateRange.value
    result = result.filter(i => {
      const date = new Date(i.startDate)
      return date >= start && date <= end
    })
  }
  return result
})

const paginatedInitiatives = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredInitiatives.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getSavingsClass = (actual: number, target: number) => {
  if (actual === undefined || target === undefined) return 'text-warning'
  return actual >= target ? 'text-success' : 'text-warning'
}

const getProgressColor = (percentage: number) => {
  if (percentage >= 100) return '#67c23a'
  if (percentage >= 70) return '#409eff'
  if (percentage >= 40) return '#e6a23c'
  return '#f56c6c'
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    completed: 'Completed',
    'in-progress': 'In Progress',
    planned: 'Planned',
    delayed: 'Delayed'
  }
  return map[status] || status
}

const getStatusTagType = (status: string) => {
  const map: Record<string, string> = {
    completed: 'success',
    'in-progress': 'primary',
    planned: 'info',
    delayed: 'danger'
  }
  return map[status] || 'info'
}

const getRankClass = (rank: number) => {
  if (rank === 1) return 'rank-gold'
  if (rank === 2) return 'rank-silver'
  if (rank === 3) return 'rank-bronze'
  return ''
}

const dateShortcuts = [
  { text: 'Last 6 Months', value: () => { const end = new Date(); const start = new Date(); start.setMonth(start.getMonth() - 6); return [start, end] } },
  { text: 'Year to Date', value: () => { const end = new Date(); const start = new Date(); start.setMonth(0, 1); return [start, end] } },
  { text: 'Last Year', value: () => { const end = new Date(); const start = new Date(); start.setFullYear(start.getFullYear() - 1); return [start, end] } }
]

// ==================== Chart Functions ====================
const generateTrendData = () => {
  if (trendPeriod.value === 'month') {
    return {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
      savings: [12.5, 15.2, 18.8, 22.4, 26.1, 30.5, 35.2, 40.8, 45.3, 49.8, 54.2, 58.5],
      target: [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120]
    }
  }
  if (trendPeriod.value === 'quarter') {
    return {
      labels: ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024', 'Q1 2025'],
      savings: [18.5, 32.2, 48.5, 62.3, 75.8],
      target: [25, 50, 75, 100, 125]
    }
  }
  return {
    labels: ['2021', '2022', '2023', '2024', '2025'],
    savings: [25.5, 48.2, 72.8, 105.3, 142.5],
    target: [30, 55, 80, 110, 150]
  }
}

const initTrendChart = () => {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()

  trendChart = echarts.init(trendChartRef.value)
  const data = generateTrendData()

  trendChart.setOption({
    tooltip: { trigger: 'axis', valueFormatter: (value: number) => '$' + value + 'k' },
    legend: { data: ['Actual Savings', 'Target Savings'], bottom: 0 },
    grid: { left: '3%', right: '4%', top: '10%', bottom: '10%', containLabel: true },
    xAxis: { type: 'category', data: data.labels },
    yAxis: { type: 'value', name: 'Savings ($k)' },
    series: [
      { name: 'Actual Savings', type: 'line', data: data.savings, smooth: true, symbol: 'circle', lineStyle: { width: 3, color: '#409eff' }, areaStyle: { opacity: 0.1, color: '#409eff' } },
      { name: 'Target Savings', type: 'line', data: data.target, smooth: true, symbol: 'diamond', lineStyle: { width: 2, color: '#67c23a', type: 'dashed' } }
    ]
  })
}

const initInitiativeChart = () => {
  if (!initiativeChartRef.value) return
  if (initiativeChart) initiativeChart.dispose()

  initiativeChart = echarts.init(initiativeChartRef.value)

  const displayInitiatives = [...initiatives.value]
      .filter(i => i.actualSavings > 0)
      .slice(0, 8)

  const names = displayInitiatives.map(i => i.name.length > 20 ? i.name.substring(0, 18) + '...' : i.name)
  const savings = displayInitiatives.map(i => (i.actualSavings || 0) / 1000)
  const colors = displayInitiatives.map(i => {
    if (i.status === 'completed') return '#67c23a'
    if (i.status === 'in-progress') return '#409eff'
    return '#909399'
  })

  initiativeChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, valueFormatter: (value: number) => value + 'k kWh' },
    grid: { left: '15%', right: '5%', top: '5%', bottom: '5%', containLabel: true },
    xAxis: { type: 'value', name: 'Savings (k kWh)' },
    yAxis: { type: 'category', data: names, axisLabel: { fontSize: 11 } },
    series: [{
      type: 'bar', data: savings,
      itemStyle: { borderRadius: [0, 4, 4, 0], color: (params: any) => colors[params.dataIndex] },
      label: { show: true, position: 'right', formatter: '{c}k kWh', fontSize: 10 }
    }]
  })
}

const initCategoryChart = () => {
  if (!categoryChartRef.value) return
  if (categoryChart) categoryChart.dispose()

  categoryChart = echarts.init(categoryChartRef.value)

  const categoryMap: Record<string, number> = {}
  initiatives.value.forEach(i => {
    const cat = i.category
    const savings = i.actualSavings || 0
    categoryMap[cat] = (categoryMap[cat] || 0) + savings
  })

  const categories = Object.keys(categoryMap)
  const savings = categories.map(c => Math.round(categoryMap[c] / 1000))

  categoryChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c}k kWh ({d}%)' },
    legend: { orient: 'vertical', left: 'left', top: 'center' },
    series: [{
      type: 'pie', radius: '55%', center: ['50%', '50%'],
      data: categories.map((name, i) => ({ name, value: savings[i] })),
      label: { show: true, formatter: '{b}: {d}%' },
      itemStyle: {
        borderRadius: 8,
        borderColor: '#fff',
        borderWidth: 2,
        color: (params: any) => {
          const colors = ['#409eff', '#67c23a', '#e6a23c', '#8b5cf6', '#f56c6c', '#909399']
          return colors[params.dataIndex % colors.length]
        }
      }
    }]
  })
}

// ==================== Actions ====================
const refreshData = async () => {
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 800))
  ElMessage.success('Savings progress data refreshed')
  initTrendChart()
  initInitiativeChart()
  initCategoryChart()
  tableLoading.value = false
}

const exportReport = () => {
  ElMessage.info('Exporting savings progress report...')
}

const fetchTrendData = () => {
  initTrendChart()
}

const handleDateChange = () => {
  currentPage.value = 1
}

const viewAllInitiatives = () => {
  ElMessage.info('Viewing all initiatives')
}

const viewAllRecommendations = () => {
  ElMessage.info('Viewing all recommendations')
}

const viewRecommendation = (rec: Recommendation) => {
  ElMessage.info(`Viewing recommendation: ${rec.title}`)
}

const acceptRecommendation = (rec: Recommendation) => {
  ElMessage.success(`Accepted recommendation: ${rec.title}`)
}

const handleSizeChange = () => { currentPage.value = 1 }
const handleCurrentChange = () => {}

// ==================== Window Resize Handler ====================
const handleResize = () => {
  trendChart?.resize()
  initiativeChart?.resize()
  categoryChart?.resize()
}

// ==================== Lifecycle ====================
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
      setTimeout(() => {
        initTrendChart()
        initInitiativeChart()
        initCategoryChart()
      }, 100)
      window.addEventListener('resize', handleResize)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  initiativeChart?.dispose()
  categoryChart?.dispose()
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

.spinner-ring:nth-child(1) { border-top-color: #3b82f6; animation-delay: 0s; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; animation-delay: 0.2s; width: 70%; height: 70%; top: 15%; left: 15%; }
.spinner-ring:nth-child(3) { border-bottom-color: #10b981; animation-delay: 0.4s; width: 40%; height: 40%; top: 30%; left: 30%; }

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

/* ==================== Main Content ==================== */
.savings-progress-page {
  padding: 24px;
  background: #f5f7fa;
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

.header-title h1 {
  font-size: 24px;
  font-weight: 600;
  color: #1f2f3d;
  margin: 0 0 4px 0;
}

.header-title .subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* KPI Cards */
.kpi-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.kpi-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: transform 0.2s, box-shadow 0.2s;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.kpi-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.kpi-card.total-savings .kpi-icon { background: #e8f8f0; color: #67c23a; }
.kpi-card.energy-saved .kpi-icon { background: #e8f4ff; color: #409eff; }
.kpi-card.progress .kpi-icon { background: #fff7e8; color: #e6a23c; }
.kpi-card.roi .kpi-icon { background: #f0e8ff; color: #8b5cf6; }

.kpi-info {
  flex: 1;
}

.kpi-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
  line-height: 1.2;
}

.kpi-value .unit {
  font-size: 14px;
  font-weight: 400;
  color: #909399;
}

.kpi-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.kpi-sub {
  font-size: 12px;
  color: #c0c4cc;
  margin-top: 2px;
}

.kpi-trend {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 13px;
  font-weight: 500;
}

.kpi-trend.positive { color: #67c23a; }
.kpi-trend.negative { color: #f56c6c; }

/* Chart Cards */
.chart-card, .table-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.card-header h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  color: #1f2f3d;
}

.chart-container {
  height: 320px;
  width: 100%;
}

.two-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

/* Table Styles */
.progress-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-percent {
  font-size: 13px;
  font-weight: 500;
  min-width: 40px;
}

.text-success {
  color: #67c23a;
  font-weight: 500;
}

.text-warning {
  color: #e6a23c;
  font-weight: 500;
}

.pagination-wrapper {
  padding: 20px 0 0;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #ebeef5;
  margin-top: 16px;
}

/* Top Initiatives Section */
.top-initiatives-section {
  background: white;
  border-radius: 16px;
  padding: 20px 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1f2f3d;
}

.initiatives-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.initiative-card {
  background: #fafafa;
  border-radius: 14px;
  padding: 16px;
  position: relative;
  transition: all 0.2s;
}

.initiative-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.card-rank {
  position: absolute;
  top: -8px;
  left: -8px;
  width: 32px;
  height: 32px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
  background: #f5f7fa;
  color: #606266;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-rank.rank-gold { background: #fff7e8; color: #e6a23c; }
.card-rank.rank-silver { background: #f0f0f0; color: #909399; }
.card-rank.rank-bronze { background: #fdf4ea; color: #cd9452; }

.card-content {
  margin-top: 8px;
}

.initiative-name {
  font-weight: 600;
  color: #1f2f3d;
  margin-bottom: 4px;
}

.initiative-category {
  font-size: 12px;
  color: #909399;
  margin-bottom: 12px;
}

.initiative-stats {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 12px;
}

.stat {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.stat-label {
  color: #909399;
}

.stat-value {
  font-weight: 500;
  color: #1f2f3d;
}

/* Recommendations Section */
.recommendations-section {
  background: white;
  border-radius: 16px;
  padding: 20px 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.recommendation-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  background: #fafafa;
  border-radius: 14px;
  transition: all 0.2s;
}

.recommendation-item:hover {
  background: #f5f7fa;
  transform: translateX(4px);
}

.rec-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.rec-icon.high {
  background: #ffe8e8;
  color: #f56c6c;
}

.rec-icon.medium {
  background: #fff7e8;
  color: #e6a23c;
}

.rec-icon.low {
  background: #e8f8f0;
  color: #67c23a;
}

.rec-content {
  flex: 1;
}

.rec-title {
  font-weight: 600;
  color: #1f2f3d;
  margin-bottom: 6px;
}

.rec-description {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.rec-metrics {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: #909399;
}

.rec-metrics .el-icon {
  vertical-align: middle;
  margin-right: 4px;
}

.rec-actions {
  opacity: 0;
  transition: opacity 0.2s;
  display: flex;
  gap: 8px;
}

.recommendation-item:hover .rec-actions {
  opacity: 1;
}

:deep(.el-table) {
  border-radius: 12px;
}

:deep(.el-table th.el-table__cell) {
  background-color: #fafafa;
  font-weight: 600;
  color: #1f2f3d;
}
</style>