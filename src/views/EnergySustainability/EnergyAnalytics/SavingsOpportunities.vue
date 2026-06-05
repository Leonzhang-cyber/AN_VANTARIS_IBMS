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
          <span class="loading-title">Savings Opportunities</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Energy Efficiency & Cost Reduction Opportunities</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="savings-opportunities-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Opportunity /></el-icon>
          Savings Opportunities
        </h1>
        <div class="page-subtitle">Identify and prioritize energy savings opportunities across your facilities</div>
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

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue">
          <el-icon><Money /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">${{ stats.totalSavings.toLocaleString() }}</div>
          <div class="stat-label">Total Potential Savings</div>
          <div class="stat-trend up">Annual</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><Lightning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalEnergySavings }}<span class="stat-unit">kWh</span></div>
          <div class="stat-label">Energy Savings</div>
          <div class="stat-trend up">Annual</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><SetUp /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.highPriority }}</div>
          <div class="stat-label">High Priority</div>
          <div class="stat-trend">Quick wins</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">
          <el-icon><Timer /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.avgPayback }}<span class="stat-unit">months</span></div>
          <div class="stat-label">Avg Payback Period</div>
          <div class="stat-trend down">↓ {{ stats.paybackReduction }} vs last year</div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Row -->
    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-title">ROI on Implemented</div>
        <div class="metric-value">{{ metrics.implementedROI }}<span class="metric-unit">%</span></div>
        <div class="metric-trend positive">↑ {{ metrics.roiGrowth }}% vs target</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Implementation Rate</div>
        <div class="metric-value">{{ metrics.implementationRate }}<span class="metric-unit">%</span></div>
        <el-progress :percentage="metrics.implementationRate" :stroke-width="8" :color="metrics.implementationRate > 70 ? '#22c55e' : (metrics.implementationRate > 40 ? '#f59e0b' : '#ef4444')" />
      </div>
      <div class="metric-card">
        <div class="metric-title">Carbon Reduction</div>
        <div class="metric-value">{{ metrics.carbonReduction }}<span class="metric-unit">tCO₂e</span></div>
        <div class="metric-trend positive">Environmental impact</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Payback Threshold</div>
        <div class="metric-value">{{ metrics.paybackThreshold }}<span class="metric-unit">months</span></div>
        <div class="metric-sub">All opportunities below threshold</div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Savings by Category</span>
          <span class="chart-subtitle">Distribution of potential savings</span>
        </div>
        <div class="chart-container" ref="savingsCategoryChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Savings vs Investment</span>
          <span class="chart-subtitle">ROI analysis</span>
        </div>
        <div class="chart-container" ref="roiChartEl"></div>
      </div>
    </div>

    <!-- Second Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Payback Period Distribution</span>
          <span class="chart-subtitle">Opportunities by payback</span>
        </div>
        <div class="chart-container" ref="paybackChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Savings Potential by Asset</span>
          <span class="chart-subtitle">Top opportunity assets</span>
        </div>
        <div class="chart-container" ref="assetChartEl"></div>
      </div>
    </div>

    <!-- Third Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Monthly Savings Forecast</span>
          <span class="chart-subtitle">Projected savings over time</span>
        </div>
        <div class="chart-container" ref="forecastChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Implementation Timeline</span>
          <span class="chart-subtitle">Recommended schedule</span>
        </div>
        <div class="chart-container" ref="timelineChartEl"></div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-input
            v-model="searchText"
            placeholder="Search by opportunity name..."
            style="width: 220px"
            clearable
            :prefix-icon="Search"
        />
        <el-select v-model="categoryFilter" placeholder="Category" clearable style="width: 140px">
          <el-option v-for="c in uniqueCategories" :key="c" :label="c" :value="c" />
        </el-select>
        <el-select v-model="priorityFilter" placeholder="Priority" clearable style="width: 120px">
          <el-option label="High" value="High" />
          <el-option label="Medium" value="Medium" />
          <el-option label="Low" value="Low" />
        </el-select>
        <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 120px">
          <el-option label="Identified" value="Identified" />
          <el-option label="In Progress" value="In Progress" />
          <el-option label="Implemented" value="Implemented" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button type="primary" link @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon> Reset Filters
        </el-button>
      </div>
    </div>

    <!-- Opportunities Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">Savings Opportunities</span>
        <el-button size="small" @click="viewAllOpportunities">View All →</el-button>
      </div>
      <el-table :data="paginatedOpportunities" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="name" label="Opportunity" min-width="200" />
        <el-table-column prop="category" label="Category" width="140">
          <template #default="{ row }">
            <el-tag :type="getCategoryTagType(row.category)" size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="estimatedSavings" label="Annual Savings" width="140">
          <template #default="{ row }">
            ${{ row.estimatedSavings.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="energySavings" label="Energy Savings" width="140">
          <template #default="{ row }">
            {{ row.energySavings.toLocaleString() }} kWh
          </template>
        </el-table-column>
        <el-table-column prop="estimatedCost" label="Est. Cost" width="140">
          <template #default="{ row }">
            ${{ row.estimatedCost.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="paybackMonths" label="Payback" width="100">
          <template #default="{ row }">
            <span :class="getPaybackClass(row.paybackMonths)">{{ row.paybackMonths }} months</span>
          </template>
        </el-table-column>
        <el-table-column prop="roi" label="ROI" width="80">
          <template #default="{ row }">
            <span :class="row.roi > 30 ? 'metric-good' : (row.roi > 15 ? 'metric-warning' : 'metric-bad')">
              {{ row.roi }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="Priority" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityTagType(row.priority)" size="small">{{ row.priority }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="140" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewOpportunityDetail(row)">Details</el-button>
            <el-button link type="success" size="small" v-if="row.status === 'Identified'" @click="implementOpportunity(row)">Implement</el-button>
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

    <!-- Opportunity Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="selectedOpportunity?.name" width="800px">
      <div v-if="selectedOpportunity" class="opportunity-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Category">{{ selectedOpportunity.category }}</el-descriptions-item>
          <el-descriptions-item label="Priority">
            <el-tag :type="getPriorityTagType(selectedOpportunity.priority)" size="small">{{ selectedOpportunity.priority }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusTagType(selectedOpportunity.status)" size="small">{{ selectedOpportunity.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Payback Period">{{ selectedOpportunity.paybackMonths }} months</el-descriptions-item>
          <el-descriptions-item label="Estimated Savings">${{ selectedOpportunity.estimatedSavings.toLocaleString() }}/year</el-descriptions-item>
          <el-descriptions-item label="Energy Savings">{{ selectedOpportunity.energySavings.toLocaleString() }} kWh/year</el-descriptions-item>
          <el-descriptions-item label="Estimated Cost">${{ selectedOpportunity.estimatedCost.toLocaleString() }}</el-descriptions-item>
          <el-descriptions-item label="ROI">{{ selectedOpportunity.roi }}%</el-descriptions-item>
          <el-descriptions-item label="Carbon Reduction">{{ selectedOpportunity.carbonReduction }} tCO₂e/year</el-descriptions-item>
          <el-descriptions-item label="Implementation Time">{{ selectedOpportunity.implementationTime }} weeks</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ selectedOpportunity.description }}</el-descriptions-item>
        </el-descriptions>

        <div class="detail-section">
          <div class="section-title">Implementation Plan</div>
          <el-timeline>
            <el-timeline-item
                v-for="step in selectedOpportunity.implementationSteps"
                :key="step.id"
                :timestamp="step.duration"
                :type="step.status === 'Completed' ? 'success' : 'primary'"
                placement="top"
            >
              {{ step.description }}
            </el-timeline-item>
          </el-timeline>
        </div>

        <div class="detail-section">
          <div class="section-title">Financial Analysis</div>
          <div class="financial-grid">
            <div class="financial-item">
              <span class="financial-label">NPV (5 years)</span>
              <span class="financial-value">${{ selectedOpportunity.npv.toLocaleString() }}</span>
            </div>
            <div class="financial-item">
              <span class="financial-label">IRR</span>
              <span class="financial-value">{{ selectedOpportunity.irr }}%</span>
            </div>
            <div class="financial-item">
              <span class="financial-label">Lifetime Savings</span>
              <span class="financial-value">${{ selectedOpportunity.lifetimeSavings.toLocaleString() }}</span>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" v-if="selectedOpportunity?.status === 'Identified'" @click="implementOpportunity(selectedOpportunity)">Implement</el-button>
        <el-button type="warning" @click="exportOpportunityReport(selectedOpportunity)">Export Report</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Opportunity, Money, Lightning, SetUp, Timer, Download, Refresh,
  Search, RefreshLeft
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading savings opportunities...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading savings opportunities...',
  'Analyzing potential savings...',
  'Calculating ROI...',
  'Prioritizing opportunities...',
  'Almost ready...'
]

// ==================== Types ====================
interface ImplementationStep {
  id: number
  description: string
  duration: string
  status: string
}

interface SavingsOpportunity {
  id: number
  name: string
  category: string
  estimatedSavings: number
  energySavings: number
  estimatedCost: number
  paybackMonths: number
  roi: number
  priority: string
  status: string
  carbonReduction: number
  implementationTime: number
  description: string
  npv: number
  irr: number
  lifetimeSavings: number
  implementationSteps: ImplementationStep[]
}

// ==================== Mock Data ====================
const generateOpportunities = (): SavingsOpportunity[] => {
  const categories = ['HVAC', 'Lighting', 'IT Equipment', 'Building Envelope', 'Controls', 'Renewable Energy']
  const statuses = ['Identified', 'In Progress', 'Implemented']
  const priorities = ['High', 'Medium', 'Low']

  const opportunities: SavingsOpportunity[] = [
    {
      id: 1, name: 'HVAC Setpoint Optimization', category: 'HVAC', estimatedSavings: 45000, energySavings: 375000,
      estimatedCost: 5000, paybackMonths: 1.3, roi: 800, priority: 'High', status: 'Identified',
      carbonReduction: 185, implementationTime: 2,
      description: 'Optimize temperature setpoints and schedules to reduce HVAC runtime while maintaining comfort levels.',
      npv: 215000, irr: 156, lifetimeSavings: 225000,
      implementationSteps: [
        { id: 1, description: 'Analyze current setpoint schedules', duration: 'Week 1', status: 'Pending' },
        { id: 2, description: 'Develop optimized schedule', duration: 'Week 2', status: 'Pending' },
        { id: 3, description: 'Implement and monitor', duration: 'Week 3-4', status: 'Pending' }
      ]
    },
    {
      id: 2, name: 'LED Lighting Retrofit', category: 'Lighting', estimatedSavings: 35000, energySavings: 292000,
      estimatedCost: 45000, paybackMonths: 15.4, roi: 78, priority: 'High', status: 'In Progress',
      carbonReduction: 145, implementationTime: 8,
      description: 'Replace fluorescent lighting with LED fixtures throughout facility.',
      npv: 125000, irr: 35, lifetimeSavings: 175000,
      implementationSteps: [
        { id: 1, description: 'Audit existing lighting', duration: 'Week 1-2', status: 'Completed' },
        { id: 2, description: 'Select LED fixtures', duration: 'Week 3-4', status: 'Completed' },
        { id: 3, description: 'Installation', duration: 'Week 5-8', status: 'In Progress' }
      ]
    },
    {
      id: 3, name: 'Server Virtualization', category: 'IT Equipment', estimatedSavings: 52000, energySavings: 433000,
      estimatedCost: 35000, paybackMonths: 8.1, roi: 148, priority: 'High', status: 'Identified',
      carbonReduction: 215, implementationTime: 12,
      description: 'Consolidate physical servers through virtualization to reduce power and cooling load.',
      npv: 245000, irr: 67, lifetimeSavings: 260000,
      implementationSteps: [
        { id: 1, description: 'Server inventory and assessment', duration: 'Week 1-3', status: 'Pending' },
        { id: 2, description: 'Virtualization planning', duration: 'Week 4-6', status: 'Pending' },
        { id: 3, description: 'Migration and decommissioning', duration: 'Week 7-12', status: 'Pending' }
      ]
    },
    {
      id: 4, name: 'VFD Installation on AHU', category: 'HVAC', estimatedSavings: 28000, energySavings: 233000,
      estimatedCost: 18000, paybackMonths: 7.7, roi: 155, priority: 'High', status: 'Identified',
      carbonReduction: 115, implementationTime: 6,
      description: 'Install variable frequency drives on air handling unit fans to optimize airflow.',
      npv: 110000, irr: 72, lifetimeSavings: 140000,
      implementationSteps: [
        { id: 1, description: 'VFD sizing and selection', duration: 'Week 1-2', status: 'Pending' },
        { id: 2, description: 'Installation', duration: 'Week 3-4', status: 'Pending' },
        { id: 3, description: 'Programming and tuning', duration: 'Week 5-6', status: 'Pending' }
      ]
    },
    {
      id: 5, name: 'Building Insulation Upgrade', category: 'Building Envelope', estimatedSavings: 22000, energySavings: 183000,
      estimatedCost: 38000, paybackMonths: 20.7, roi: 58, priority: 'Medium', status: 'Identified',
      carbonReduction: 91, implementationTime: 10,
      description: 'Add insulation to roof and walls to reduce heat transfer and HVAC load.',
      npv: 72000, irr: 25, lifetimeSavings: 110000,
      implementationSteps: [
        { id: 1, description: 'Thermal imaging survey', duration: 'Week 1-2', status: 'Pending' },
        { id: 2, description: 'Material selection', duration: 'Week 3-4', status: 'Pending' },
        { id: 3, description: 'Installation', duration: 'Week 5-10', status: 'Pending' }
      ]
    },
    {
      id: 6, name: 'Solar PV Installation', category: 'Renewable Energy', estimatedSavings: 65000, energySavings: 542000,
      estimatedCost: 250000, paybackMonths: 46.2, roi: 26, priority: 'Medium', status: 'Identified',
      carbonReduction: 270, implementationTime: 20,
      description: 'Install rooftop solar photovoltaic system to generate renewable energy.',
      npv: 180000, irr: 12, lifetimeSavings: 325000,
      implementationSteps: [
        { id: 1, description: 'Feasibility study', duration: 'Week 1-4', status: 'Pending' },
        { id: 2, description: 'Design and permitting', duration: 'Week 5-10', status: 'Pending' },
        { id: 3, description: 'Installation', duration: 'Week 11-18', status: 'Pending' },
        { id: 4, description: 'Commissioning', duration: 'Week 19-20', status: 'Pending' }
      ]
    },
    {
      id: 7, name: 'Demand Control Ventilation', category: 'Controls', estimatedSavings: 18000, energySavings: 150000,
      estimatedCost: 12000, paybackMonths: 8.0, roi: 150, priority: 'High', status: 'In Progress',
      carbonReduction: 75, implementationTime: 5,
      description: 'Install CO2 sensors to modulate outside air based on occupancy.',
      npv: 78000, irr: 68, lifetimeSavings: 90000,
      implementationSteps: [
        { id: 1, description: 'Sensor placement plan', duration: 'Week 1', status: 'Completed' },
        { id: 2, description: 'Sensor installation', duration: 'Week 2-3', status: 'Completed' },
        { id: 3, description: 'System integration', duration: 'Week 4-5', status: 'In Progress' }
      ]
    },
    {
      id: 8, name: 'Chiller Efficiency Upgrade', category: 'HVAC', estimatedSavings: 35000, energySavings: 292000,
      estimatedCost: 55000, paybackMonths: 18.9, roi: 64, priority: 'Medium', status: 'Identified',
      carbonReduction: 145, implementationTime: 12,
      description: 'Upgrade chiller controls and optimize condenser water temperature.',
      npv: 95000, irr: 28, lifetimeSavings: 175000,
      implementationSteps: [
        { id: 1, description: 'Performance assessment', duration: 'Week 1-3', status: 'Pending' },
        { id: 2, description: 'Control upgrade', duration: 'Week 4-8', status: 'Pending' },
        { id: 3, description: 'Optimization tuning', duration: 'Week 9-12', status: 'Pending' }
      ]
    },
    {
      id: 9, name: 'Power Factor Correction', category: 'Electrical', estimatedSavings: 12000, energySavings: 100000,
      estimatedCost: 8000, paybackMonths: 8.0, roi: 150, priority: 'High', status: 'Identified',
      carbonReduction: 50, implementationTime: 4,
      description: 'Install power factor correction capacitors to reduce reactive power charges.',
      npv: 52000, irr: 65, lifetimeSavings: 60000,
      implementationSteps: [
        { id: 1, description: 'Power quality audit', duration: 'Week 1', status: 'Pending' },
        { id: 2, description: 'Capacitor sizing', duration: 'Week 2', status: 'Pending' },
        { id: 3, description: 'Installation', duration: 'Week 3-4', status: 'Pending' }
      ]
    },
    {
      id: 10, name: 'Occupancy Sensors for Lighting', category: 'Lighting', estimatedSavings: 15000, energySavings: 125000,
      estimatedCost: 15000, paybackMonths: 12.0, roi: 100, priority: 'Medium', status: 'Identified',
      carbonReduction: 62, implementationTime: 6,
      description: 'Install occupancy sensors in low-traffic areas to automatically control lighting.',
      npv: 65000, irr: 45, lifetimeSavings: 75000,
      implementationSteps: [
        { id: 1, description: 'Area assessment', duration: 'Week 1-2', status: 'Pending' },
        { id: 2, description: 'Sensor selection', duration: 'Week 3', status: 'Pending' },
        { id: 3, description: 'Installation', duration: 'Week 4-6', status: 'Pending' }
      ]
    }
  ]

  return opportunities
}

const opportunities = ref<SavingsOpportunity[]>(generateOpportunities())

// ==================== State ====================
const searchText = ref('')
const categoryFilter = ref('')
const priorityFilter = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)
const selectedOpportunity = ref<SavingsOpportunity | null>(null)

// Chart refs
let savingsCategoryChart: echarts.ECharts | null = null
let roiChart: echarts.ECharts | null = null
let paybackChart: echarts.ECharts | null = null
let assetChart: echarts.ECharts | null = null
let forecastChart: echarts.ECharts | null = null
let timelineChart: echarts.ECharts | null = null

const savingsCategoryChartEl = ref<HTMLElement | null>(null)
const roiChartEl = ref<HTMLElement | null>(null)
const paybackChartEl = ref<HTMLElement | null>(null)
const assetChartEl = ref<HTMLElement | null>(null)
const forecastChartEl = ref<HTMLElement | null>(null)
const timelineChartEl = ref<HTMLElement | null>(null)

// ==================== Computed ====================
const stats = computed(() => {
  const identified = opportunities.value.filter(o => o.status === 'Identified')
  const totalSavings = identified.reduce((sum, o) => sum + o.estimatedSavings, 0)
  const totalEnergySavings = identified.reduce((sum, o) => sum + o.energySavings, 0)
  const highPriority = identified.filter(o => o.priority === 'High').length
  const avgPayback = identified.reduce((sum, o) => sum + o.paybackMonths, 0) / identified.length

  return {
    totalSavings: Math.round(totalSavings),
    totalEnergySavings: Math.round(totalEnergySavings),
    highPriority: highPriority,
    avgPayback: Math.round(avgPayback),
    paybackReduction: 15
  }
})

const metrics = computed(() => {
  const implemented = opportunities.value.filter(o => o.status === 'Implemented')
  const avgRoi = implemented.reduce((sum, o) => sum + o.roi, 0) / (implemented.length || 1)
  const implementationRate = Math.round((implemented.length / opportunities.value.length) * 100)
  const carbonReduction = implemented.reduce((sum, o) => sum + o.carbonReduction, 0)

  return {
    implementedROI: Math.round(avgRoi),
    roiGrowth: 12,
    implementationRate: implementationRate,
    carbonReduction: carbonReduction,
    paybackThreshold: 24
  }
})

const uniqueCategories = computed(() => {
  return [...new Set(opportunities.value.map(o => o.category))]
})

const filteredOpportunities = computed(() => {
  let filtered = [...opportunities.value]

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(o =>
        o.name.toLowerCase().includes(search) ||
        o.category.toLowerCase().includes(search)
    )
  }

  if (categoryFilter.value) {
    filtered = filtered.filter(o => o.category === categoryFilter.value)
  }

  if (priorityFilter.value) {
    filtered = filtered.filter(o => o.priority === priorityFilter.value)
  }

  if (statusFilter.value) {
    filtered = filtered.filter(o => o.status === statusFilter.value)
  }

  return filtered
})

const totalRecords = computed(() => filteredOpportunities.value.length)

const paginatedOpportunities = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredOpportunities.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getCategoryTagType = (category: string): string => {
  const map: Record<string, string> = {
    'HVAC': 'danger', 'Lighting': 'warning', 'IT Equipment': 'primary',
    'Building Envelope': 'info', 'Controls': 'success', 'Renewable Energy': '',
    'Electrical': 'primary'
  }
  return map[category] || 'info'
}

const getPriorityTagType = (priority: string): string => {
  const map: Record<string, string> = { High: 'danger', Medium: 'warning', Low: 'info' }
  return map[priority] || 'info'
}

const getStatusTagType = (status: string): string => {
  const map: Record<string, string> = { Identified: 'warning', 'In Progress': 'primary', Implemented: 'success' }
  return map[status] || 'info'
}

const getPaybackClass = (payback: number): string => {
  if (payback <= 12) return 'metric-good'
  if (payback <= 24) return 'metric-warning'
  return 'metric-bad'
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
const initSavingsCategoryChart = () => {
  if (!savingsCategoryChartEl.value) return
  if (savingsCategoryChart) {
    savingsCategoryChart.dispose()
    savingsCategoryChart = null
  }

  const categoryMap = new Map<string, number>()
  opportunities.value.forEach(o => {
    categoryMap.set(o.category, (categoryMap.get(o.category) || 0) + o.estimatedSavings)
  })

  const data = Array.from(categoryMap.entries()).map(([name, value]) => ({ name, value: Math.round(value / 1000) }))

  savingsCategoryChart = echarts.init(savingsCategoryChartEl.value)
  savingsCategoryChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: ${c}K ({d}%)' },
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

const initRoiChart = () => {
  if (!roiChartEl.value) return
  if (roiChart) {
    roiChart.dispose()
    roiChart = null
  }

  const opportunities_with_roi = opportunities.value.filter(o => o.roi <= 200).slice(0, 8)
  const names = opportunities_with_roi.map(o => o.name.length > 15 ? o.name.slice(0, 15) + '...' : o.name)
  const rois = opportunities_with_roi.map(o => o.roi)
  const paybacks = opportunities_with_roi.map(o => o.paybackMonths)

  roiChart = echarts.init(roiChartEl.value)
  roiChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['ROI (%)', 'Payback (months)'], bottom: 0 },
    grid: { top: 40, left: 60, right: 60, bottom: 40 },
    xAxis: { type: 'category', data: names, axisLabel: { rotate: 30, fontSize: 10 } },
    yAxis: [
      { type: 'value', name: 'ROI (%)', position: 'left' },
      { type: 'value', name: 'Payback (months)', position: 'right' }
    ],
    series: [
      { name: 'ROI (%)', type: 'bar', data: rois, itemStyle: { color: '#22c55e', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top', formatter: '{c}%' } },
      { name: 'Payback (months)', type: 'line', data: paybacks, lineStyle: { color: '#ef4444', width: 2 }, symbol: 'circle', yAxisIndex: 1 }
    ]
  })
}

const initPaybackChart = () => {
  if (!paybackChartEl.value) return
  if (paybackChart) {
    paybackChart.dispose()
    paybackChart = null
  }

  const ranges = ['<6 months', '6-12 months', '12-18 months', '18-24 months', '>24 months']
  const counts = [2, 3, 2, 2, 1]

  paybackChart = echarts.init(paybackChartEl.value)
  paybackChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: ranges },
    yAxis: { type: 'value', name: 'Number of Opportunities' },
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

const initAssetChart = () => {
  if (!assetChartEl.value) return
  if (assetChart) {
    assetChart.dispose()
    assetChart = null
  }

  const topAssets = opportunities.value.slice(0, 6)
  const names = topAssets.map(o => o.name.length > 15 ? o.name.slice(0, 15) + '...' : o.name)
  const savings = topAssets.map(o => o.estimatedSavings / 1000)

  assetChart = echarts.init(assetChartEl.value)
  assetChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: '{b}<br/>Savings: ${c}K' },
    grid: { top: 30, left: 50, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: names, axisLabel: { rotate: 30, fontSize: 11 } },
    yAxis: { type: 'value', name: 'Annual Savings ($K)' },
    series: [{
      type: 'bar',
      data: savings,
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#3b82f6' },
      label: { show: true, position: 'top', formatter: '${c}K' }
    }]
  })
}

const initForecastChart = () => {
  if (!forecastChartEl.value) return
  if (forecastChart) {
    forecastChart.dispose()
    forecastChart = null
  }

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const cumulativeSavings = [12, 28, 48, 72, 100, 135, 175, 220, 270, 325, 385, 450]

  forecastChart = echarts.init(forecastChartEl.value)
  forecastChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'Cumulative Savings ($K)' },
    series: [{
      type: 'line',
      data: cumulativeSavings,
      smooth: true,
      lineStyle: { color: '#22c55e', width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      areaStyle: { opacity: 0.1, color: '#22c55e' },
      label: { show: true, position: 'top', formatter: '${c}K' }
    }]
  })
}

const initTimelineChart = () => {
  if (!timelineChartEl.value) return
  if (timelineChart) {
    timelineChart.dispose()
    timelineChart = null
  }

  const quarters = ['Q1', 'Q2', 'Q3', 'Q4']
  const highPriority = [3, 2, 1, 0]
  const mediumPriority = [1, 2, 1, 1]
  const lowPriority = [0, 0, 1, 1]

  timelineChart = echarts.init(timelineChartEl.value)
  timelineChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['High Priority', 'Medium Priority', 'Low Priority'], bottom: 0 },
    grid: { top: 30, left: 50, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: quarters },
    yAxis: { type: 'value', name: 'Number of Opportunities' },
    series: [
      { name: 'High Priority', type: 'bar', stack: 'total', data: highPriority, itemStyle: { color: '#ef4444' }, label: { show: true, position: 'inside' } },
      { name: 'Medium Priority', type: 'bar', stack: 'total', data: mediumPriority, itemStyle: { color: '#f59e0b' }, label: { show: true, position: 'inside' } },
      { name: 'Low Priority', type: 'bar', stack: 'total', data: lowPriority, itemStyle: { color: '#3b82f6' }, label: { show: true, position: 'inside' } }
    ]
  })
}

const refreshCharts = () => {
  nextTick(() => {
    initSavingsCategoryChart()
    initRoiChart()
    initPaybackChart()
    initAssetChart()
    initForecastChart()
    initTimelineChart()
  })
}

// ==================== Actions ====================
const viewOpportunityDetail = (opportunity: SavingsOpportunity) => {
  selectedOpportunity.value = opportunity
  detailDialogVisible.value = true
}

const viewAllOpportunities = () => {
  ElMessage.info('Viewing all opportunities')
}

const implementOpportunity = (opportunity: SavingsOpportunity | null) => {
  if (opportunity) {
    ElMessage.success(`Implementation started for ${opportunity.name}`)
  }
}

const exportOpportunityReport = (opportunity: SavingsOpportunity | null) => {
  if (opportunity) {
    ElMessage.success(`Exporting report for ${opportunity.name}...`)
  }
}

const exportData = () => {
  ElMessage.success('Exporting savings opportunities data...')
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
    const charts = [savingsCategoryChart, roiChart, paybackChart, assetChart, forecastChart, timelineChart]
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
  const charts = [savingsCategoryChart, roiChart, paybackChart, assetChart, forecastChart, timelineChart]
  charts.forEach(chart => {
    if (chart && !chart.isDisposed()) chart.dispose()
  })
})
</script>

<style scoped>
.savings-opportunities-page {
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
.stat-trend.down { color: #22c55e; }

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
  height: 300px;
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

/* Opportunity Detail */
.opportunity-detail {
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

.financial-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
}

.financial-item {
  text-align: center;
}

.financial-label {
  display: block;
  font-size: 12px;
  color: #64748b;
  margin-bottom: 4px;
}

.financial-value {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
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
  .financial-grid {
    grid-template-columns: 1fr;
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