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
          <span class="loading-title">ESG Dashboard</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Environmental, Social & Governance Performance</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="esg-dashboard-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><DataAnalysis /></el-icon>
          ESG Dashboard
        </h1>
        <div class="page-subtitle">Environmental, Social & Governance performance metrics and compliance tracking</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="exportData">
          <el-icon><Download /></el-icon> Export Report
        </el-button>
        <el-button @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon> Refresh
        </el-button>
      </div>
    </div>

    <!-- Overall Score Card -->
    <div class="overall-score">
      <div class="score-ring">
        <div class="score-value">{{ overallScore.overall }}</div>
        <div class="score-label">Overall ESG Score</div>
        <div class="score-rating">{{ overallScore.rating }}</div>
      </div>
      <div class="score-breakdown">
        <div class="score-item">
          <div class="score-item-header">
            <span class="score-item-label">Environmental</span>
            <span class="score-item-value">{{ overallScore.environmental }}</span>
          </div>
          <el-progress :percentage="overallScore.environmental" :stroke-width="8" :color="'#22c55e'" />
        </div>
        <div class="score-item">
          <div class="score-item-header">
            <span class="score-item-label">Social</span>
            <span class="score-item-value">{{ overallScore.social }}</span>
          </div>
          <el-progress :percentage="overallScore.social" :stroke-width="8" :color="'#3b82f6'" />
        </div>
        <div class="score-item">
          <div class="score-item-header">
            <span class="score-item-label">Governance</span>
            <span class="score-item-value">{{ overallScore.governance }}</span>
          </div>
          <el-progress :percentage="overallScore.governance" :stroke-width="8" :color="'#8b5cf6'" />
        </div>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.carbonReduction }}<span class="stat-unit">%</span></div>
          <div class="stat-label">Carbon Reduction</div>
          <div class="stat-trend up">vs 2023 baseline</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon blue">
          <el-icon><Sunny /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.renewableEnergy }}<span class="stat-unit">%</span></div>
          <div class="stat-label">Renewable Energy</div>
          <div class="stat-trend up">↑ {{ stats.renewableGrowth }}% YoY</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><User /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.diversityIndex }}<span class="stat-unit">%</span></div>
          <div class="stat-label">Diversity & Inclusion</div>
          <div class="stat-trend up">↑ {{ stats.diversityGrowth }}% YoY</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.complianceRate }}<span class="stat-unit">%</span></div>
          <div class="stat-label">Compliance Rate</div>
          <div class="stat-trend up">↑ {{ stats.complianceGrowth }}% YoY</div>
        </div>
      </div>
    </div>

    <!-- Charts Row 1 -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Carbon Emissions Trend</span>
          <span class="chart-subtitle">Scope 1,2,3 over time</span>
        </div>
        <div class="chart-container" ref="carbonChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Energy Mix</span>
          <span class="chart-subtitle">Renewable vs Non-renewable</span>
        </div>
        <div class="chart-container" ref="energyChartEl"></div>
      </div>
    </div>

    <!-- Charts Row 2 -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Social Impact Metrics</span>
          <span class="chart-subtitle">Community & Employee indicators</span>
        </div>
        <div class="chart-container" ref="socialChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Governance KPIs</span>
          <span class="chart-subtitle">Board diversity & ethics</span>
        </div>
        <div class="chart-container" ref="governanceChartEl"></div>
      </div>
    </div>

    <!-- Charts Row 3 -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">ESG Performance vs Peers</span>
          <span class="chart-subtitle">Industry benchmark</span>
        </div>
        <div class="chart-container" ref="peerChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">SDG Contribution</span>
          <span class="chart-subtitle">UN Sustainable Development Goals</span>
        </div>
        <div class="chart-container" ref="sdgChartEl"></div>
      </div>
    </div>

    <!-- ESG Compliance Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">ESG Compliance Summary</span>
        <el-button size="small" @click="viewAllCompliance">View All →</el-button>
      </div>
      <el-table :data="paginatedCompliance" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="framework" label="Framework" min-width="180" />
        <el-table-column prop="requirement" label="Requirement" min-width="250" />
        <el-table-column prop="status" label="Status" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="Progress" width="150">
          <template #default="{ row }">
            <el-progress :percentage="row.progress" :stroke-width="8" :color="getProgressColor(row.progress)" />
          </template>
        </el-table-column>
        <el-table-column prop="dueDate" label="Due Date" width="120" />
        <el-table-column label="Actions" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDetail(row)">Details</el-button>
            <el-button link type="success" size="small" @click="updateStatus(row)">Update</el-button>
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

    <!-- Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="selectedItem?.framework + ' - ' + selectedItem?.requirement" width="700px">
      <div v-if="selectedItem" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Framework">{{ selectedItem.framework }}</el-descriptions-item>
          <el-descriptions-item label="Requirement">{{ selectedItem.requirement }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusTagType(selectedItem.status)" size="small">{{ selectedItem.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Progress">{{ selectedItem.progress }}%</el-descriptions-item>
          <el-descriptions-item label="Due Date">{{ selectedItem.dueDate }}</el-descriptions-item>
          <el-descriptions-item label="Assigned To">{{ selectedItem.assignedTo }}</el-descriptions-item>
          <el-descriptions-item label="Last Updated">{{ selectedItem.lastUpdated }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ selectedItem.description }}</el-descriptions-item>
        </el-descriptions>

        <div class="detail-section">
          <div class="section-title">Evidence & Documents</div>
          <el-table :data="selectedItem.documents" border stripe>
            <el-table-column prop="name" label="Document Name" min-width="250" />
            <el-table-column prop="date" label="Upload Date" width="120" />
            <el-table-column label="Action" width="80">
              <template #default>
                <el-button link type="primary" size="small">View</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="updateStatus(selectedItem)">Update Status</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  DataAnalysis, TrendCharts, Sunny, User, Document, Download, Refresh
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading ESG dashboard...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading ESG metrics...',
  'Fetching compliance data...',
  'Calculating scores...',
  'Preparing dashboard...',
  'Almost ready...'
]

// ==================== Types ====================
interface ComplianceItem {
  id: number
  framework: string
  requirement: string
  status: string
  progress: number
  dueDate: string
  assignedTo: string
  lastUpdated: string
  description: string
  documents: { name: string; date: string }[]
}

// ==================== Mock Data ====================
const overallScore = {
  overall: 78,
  rating: 'Good',
  environmental: 82,
  social: 74,
  governance: 76
}

const stats = {
  carbonReduction: 24,
  renewableEnergy: 42,
  renewableGrowth: 8,
  diversityIndex: 68,
  diversityGrowth: 5,
  complianceRate: 94,
  complianceGrowth: 3
}

const complianceData: ComplianceItem[] = [
  {
    id: 1, framework: 'GRI', requirement: 'Disclosure 302-1: Energy consumption within organization',
    status: 'Compliant', progress: 100, dueDate: '2024-03-15', assignedTo: 'Energy Team',
    lastUpdated: '2024-03-10', description: 'Annual energy consumption report submitted',
    documents: [{ name: 'Energy_Report_2023.pdf', date: '2024-03-10' }]
  },
  {
    id: 2, framework: 'GRI', requirement: 'Disclosure 305-1: Direct (Scope 1) GHG emissions',
    status: 'In Progress', progress: 75, dueDate: '2024-04-30', assignedTo: 'Carbon Team',
    lastUpdated: '2024-04-15', description: 'Scope 1 emissions calculation in progress',
    documents: [{ name: 'Scope1_Calculation.xlsx', date: '2024-04-15' }]
  },
  {
    id: 3, framework: 'GRI', requirement: 'Disclosure 405-1: Diversity of governance bodies',
    status: 'Compliant', progress: 100, dueDate: '2024-02-28', assignedTo: 'HR',
    lastUpdated: '2024-02-25', description: 'Board diversity report completed',
    documents: [{ name: 'Diversity_Report_2024.pdf', date: '2024-02-25' }]
  },
  {
    id: 4, framework: 'TCFD', requirement: 'Governance: Board oversight of climate risks',
    status: 'In Progress', progress: 60, dueDate: '2024-06-30', assignedTo: 'Risk Committee',
    lastUpdated: '2024-05-20', description: 'Climate governance framework being established',
    documents: [{ name: 'TCFD_Framework.docx', date: '2024-05-20' }]
  },
  {
    id: 5, framework: 'TCFD', requirement: 'Strategy: Climate-related risks and opportunities',
    status: 'Not Started', progress: 20, dueDate: '2024-09-30', assignedTo: 'Strategy Team',
    lastUpdated: '2024-05-01', description: 'Initial risk assessment completed',
    documents: [{ name: 'Risk_Assessment_Summary.pdf', date: '2024-05-01' }]
  },
  {
    id: 6, framework: 'SASB', requirement: 'GHG emissions - Data centers',
    status: 'Compliant', progress: 100, dueDate: '2024-03-31', assignedTo: 'Operations',
    lastUpdated: '2024-03-28', description: 'Data center emissions reported',
    documents: [{ name: 'DC_Emissions_2023.csv', date: '2024-03-28' }]
  },
  {
    id: 7, framework: 'SASB', requirement: 'Energy management - Power usage effectiveness',
    status: 'In Progress', progress: 85, dueDate: '2024-05-31', assignedTo: 'Facilities',
    lastUpdated: '2024-05-15', description: 'Monthly PUE tracking implemented',
    documents: [{ name: 'PUE_Tracking.xlsx', date: '2024-05-15' }]
  },
  {
    id: 8, framework: 'UNGC', requirement: 'Human rights assessment',
    status: 'In Progress', progress: 50, dueDate: '2024-07-31', assignedTo: 'Compliance',
    lastUpdated: '2024-06-01', description: 'Supply chain human rights mapping in progress',
    documents: [{ name: 'Human_Rights_Policy.pdf', date: '2024-06-01' }]
  },
  {
    id: 9, framework: 'UNGC', requirement: 'Anti-corruption policy',
    status: 'Compliant', progress: 100, dueDate: '2024-01-31', assignedTo: 'Legal',
    lastUpdated: '2024-01-28', description: 'Anti-corruption policy updated and communicated',
    documents: [{ name: 'Anti_Corruption_Policy_2024.pdf', date: '2024-01-28' }]
  },
  {
    id: 10, framework: 'CSRD', requirement: 'ESRS E1 - Climate change',
    status: 'Not Started', progress: 10, dueDate: '2025-12-31', assignedTo: 'ESG Team',
    lastUpdated: '2024-04-01', description: 'Preliminary gap analysis completed',
    documents: [{ name: 'CSRD_Gap_Analysis.pdf', date: '2024-04-01' }]
  }
]

// ==================== State ====================
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)
const selectedItem = ref<ComplianceItem | null>(null)

// Chart refs
let carbonChart: echarts.ECharts | null = null
let energyChart: echarts.ECharts | null = null
let socialChart: echarts.ECharts | null = null
let governanceChart: echarts.ECharts | null = null
let peerChart: echarts.ECharts | null = null
let sdgChart: echarts.ECharts | null = null

const carbonChartEl = ref<HTMLElement | null>(null)
const energyChartEl = ref<HTMLElement | null>(null)
const socialChartEl = ref<HTMLElement | null>(null)
const governanceChartEl = ref<HTMLElement | null>(null)
const peerChartEl = ref<HTMLElement | null>(null)
const sdgChartEl = ref<HTMLElement | null>(null)

// ==================== Computed ====================
const filteredCompliance = computed(() => {
  return [...complianceData]
})

const totalRecords = computed(() => filteredCompliance.value.length)

const paginatedCompliance = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredCompliance.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getStatusTagType = (status: string): string => {
  const map: Record<string, string> = { Compliant: 'success', 'In Progress': 'warning', 'Not Started': 'info' }
  return map[status] || 'info'
}

const getProgressColor = (progress: number): string => {
  if (progress >= 80) return '#22c55e'
  if (progress >= 40) return '#f59e0b'
  return '#ef4444'
}

// ==================== Chart Functions ====================
const initCarbonChart = () => {
  if (!carbonChartEl.value) return
  if (carbonChart) {
    carbonChart.dispose()
    carbonChart = null
  }

  const years = ['2020', '2021', '2022', '2023', '2024']
  const scope1 = [12500, 11800, 11200, 10500, 9800]
  const scope2 = [18500, 17800, 16500, 15200, 14200]
  const scope3 = [22500, 21800, 20800, 19500, 18500]

  carbonChart = echarts.init(carbonChartEl.value)
  carbonChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Scope 1', 'Scope 2', 'Scope 3'], bottom: 0 },
    grid: { top: 40, left: 60, right: 30, bottom: 40 },
    xAxis: { type: 'category', data: years },
    yAxis: { type: 'value', name: 'Emissions (tCO₂e)' },
    series: [
      { name: 'Scope 1', type: 'line', data: scope1, lineStyle: { color: '#f59e0b', width: 2 }, symbol: 'circle', areaStyle: { opacity: 0.1 } },
      { name: 'Scope 2', type: 'line', data: scope2, lineStyle: { color: '#3b82f6', width: 2 }, symbol: 'circle', areaStyle: { opacity: 0.1 } },
      { name: 'Scope 3', type: 'line', data: scope3, lineStyle: { color: '#22c55e', width: 2 }, symbol: 'circle', areaStyle: { opacity: 0.1 } }
    ]
  })
}

const initEnergyChart = () => {
  if (!energyChartEl.value) return
  if (energyChart) {
    energyChart.dispose()
    energyChart = null
  }

  energyChart = echarts.init(energyChartEl.value)
  energyChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}%' },
    legend: { orient: 'vertical', left: 'left', data: ['Renewable', 'Natural Gas', 'Coal', 'Nuclear'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { value: 42, name: 'Renewable', itemStyle: { color: '#22c55e' } },
        { value: 35, name: 'Natural Gas', itemStyle: { color: '#f59e0b' } },
        { value: 15, name: 'Coal', itemStyle: { color: '#ef4444' } },
        { value: 8, name: 'Nuclear', itemStyle: { color: '#3b82f6' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  })
}

const initSocialChart = () => {
  if (!socialChartEl.value) return
  if (socialChart) {
    socialChart.dispose()
    socialChart = null
  }

  const metrics = ['Female Leadership', 'Local Hiring', 'Training Hours', 'Community Investment', 'Health & Safety']
  const values = [38, 85, 42, 65, 92]

  socialChart = echarts.init(socialChartEl.value)
  socialChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 60, right: 20, bottom: 40, containLabel: true },
    xAxis: { type: 'category', data: metrics, axisLabel: { rotate: 30, fontSize: 11 } },
    yAxis: { type: 'value', name: 'Percentage (%)', max: 100 },
    series: [{
      type: 'bar',
      data: values,
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#3b82f6' },
      label: { show: true, position: 'top', formatter: '{c}%' }
    }]
  })
}

const initGovernanceChart = () => {
  if (!governanceChartEl.value) return
  if (governanceChart) {
    governanceChart.dispose()
    governanceChart = null
  }

  const metrics = ['Board Independence', 'Audit Compliance', 'Ethics Training', 'Whistleblower Protection', 'Risk Oversight']
  const values = [85, 100, 92, 88, 78]

  governanceChart = echarts.init(governanceChartEl.value)
  governanceChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 60, right: 20, bottom: 40, containLabel: true },
    xAxis: { type: 'category', data: metrics, axisLabel: { rotate: 30, fontSize: 11 } },
    yAxis: { type: 'value', name: 'Percentage (%)', max: 100 },
    series: [{
      type: 'bar',
      data: values,
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#8b5cf6' },
      label: { show: true, position: 'top', formatter: '{c}%' }
    }]
  })
}

const initPeerChart = () => {
  if (!peerChartEl.value) return
  if (peerChart) {
    peerChart.dispose()
    peerChart = null
  }

  const peers = ['Our Company', 'Peer A', 'Peer B', 'Peer C', 'Industry Avg']
  const scores = [78, 82, 75, 80, 76]

  peerChart = echarts.init(peerChartEl.value)
  peerChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 60, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: peers, axisLabel: { rotate: 30 } },
    yAxis: { type: 'value', name: 'ESG Score', min: 60, max: 90 },
    series: [{
      type: 'bar',
      data: scores,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          return params.name === 'Our Company' ? '#3b82f6' : '#94a3b8'
        }
      },
      label: { show: true, position: 'top' }
    }]
  })
}

const initSdgChart = () => {
  if (!sdgChartEl.value) return
  if (sdgChart) {
    sdgChart.dispose()
    sdgChart = null
  }

  const sdgs = ['SDG 7', 'SDG 8', 'SDG 9', 'SDG 11', 'SDG 12', 'SDG 13']
  const scores = [85, 72, 78, 68, 82, 75]

  sdgChart = echarts.init(sdgChartEl.value)
  sdgChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 60, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: sdgs },
    yAxis: { type: 'value', name: 'Contribution Score', max: 100 },
    series: [{
      type: 'bar',
      data: scores,
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#22c55e' },
      label: { show: true, position: 'top' }
    }]
  })
}

const refreshCharts = () => {
  nextTick(() => {
    initCarbonChart()
    initEnergyChart()
    initSocialChart()
    initGovernanceChart()
    initPeerChart()
    initSdgChart()
  })
}

// ==================== Actions ====================
const viewDetail = (item: ComplianceItem) => {
  selectedItem.value = item
  detailDialogVisible.value = true
}

const updateStatus = (item: ComplianceItem | null) => {
  if (item) {
    ElMessage.success(`Status updated for ${item.requirement}`)
  }
}

const viewAllCompliance = () => {
  ElMessage.info('Viewing all compliance items')
}

const exportData = () => {
  ElMessage.success('Exporting ESG dashboard data...')
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
    const charts = [carbonChart, energyChart, socialChart, governanceChart, peerChart, sdgChart]
    charts.forEach(chart => {
      if (chart && !chart.isDisposed()) chart.resize()
    })
  }, 100)
}

// ==================== Watch ====================
watch([currentPage], () => {
  // Pagination change handler
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
  const charts = [carbonChart, energyChart, socialChart, governanceChart, peerChart, sdgChart]
  charts.forEach(chart => {
    if (chart && !chart.isDisposed()) chart.dispose()
  })
})
</script>

<style scoped>
.esg-dashboard-page {
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

/* Overall Score */
.overall-score {
  display: flex;
  gap: 40px;
  background: white;
  border-radius: 24px;
  padding: 24px 32px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  align-items: center;
  flex-wrap: wrap;
}

.score-ring {
  text-align: center;
  position: relative;
}

.score-value {
  font-size: 56px;
  font-weight: 700;
  color: #1e293b;
}

.score-label {
  font-size: 14px;
  color: #64748b;
  margin-top: 4px;
}

.score-rating {
  font-size: 12px;
  color: #22c55e;
  margin-top: 4px;
  font-weight: 500;
}

.score-breakdown {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.score-item-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.score-item-label {
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
}

.score-item-value {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
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

.stat-icon.green { background: #dcfce7; color: #22c55e; }
.stat-icon.blue { background: #eef2ff; color: #3b82f6; }
.stat-icon.orange { background: #fef3c7; color: #f59e0b; }
.stat-icon.purple { background: #f3e8ff; color: #8b5cf6; }

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
}

.stat-unit {
  font-size: 14px;
  font-weight: normal;
  color: #64748b;
  margin-left: 4px;
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
  flex-wrap: wrap;
  gap: 12px;
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

/* Detail Content */
.detail-content {
  padding: 8px;
}

.detail-section {
  margin-top: 24px;
}

.section-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
  margin-bottom: 16px;
  padding-left: 10px;
  border-left: 3px solid #3b82f6;
}

/* Responsive */
@media (max-width: 1000px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .charts-row {
    flex-direction: column;
  }
  .overall-score {
    flex-direction: column;
    text-align: center;
  }
}

@media (max-width: 768px) {
  .stats-grid {
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
  .filter-left .el-select,
  .filter-left .el-date-editor {
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
  max-height: 550px;
  overflow-y: auto;
}
:deep(.el-progress-bar__inner) {
  border-radius: 4px;
}
</style>