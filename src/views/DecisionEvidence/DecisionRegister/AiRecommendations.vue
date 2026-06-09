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
        <div class="loading-tip">AI Recommendations Register</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="ai-recommendations-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Decision & Evidence</el-breadcrumb-item>
            <el-breadcrumb-item>Decision Register</el-breadcrumb-item>
            <el-breadcrumb-item>AI Recommendations</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>AI Recommendations</h1>
        <p class="description">AI-powered insights and recommendations for operational optimization, predictive maintenance, and energy efficiency</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export
        </el-button>
        <el-button type="primary" @click="handleRunAIAnalysis">
          <el-icon><Cpu /></el-icon>
          Run AI Analysis
        </el-button>
      </div>
    </div>

    <!-- AI Confidence & Impact Charts -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :lg="14">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>AI Recommendation Confidence Trend</span>
              <el-radio-group v-model="confidencePeriod" size="small">
                <el-radio-button value="weekly">Weekly</el-radio-button>
                <el-radio-button value="monthly">Monthly</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="confidenceChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="10">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Recommendations by Category</span>
            </div>
          </template>
          <div ref="categoryChartRef" class="chart-container-small"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Stats Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6" v-for="stat in statsCards" :key="stat.title">
        <el-card class="stat-card" shadow="hover" @click="handleCardClick(stat)">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-title">{{ stat.title }}</div>
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-trend" :class="stat.trend > 0 ? 'up' : 'down'">
                <el-icon><component :is="stat.trend > 0 ? 'ArrowUp' : 'ArrowDown'" /></el-icon>
                {{ Math.abs(stat.trend) }}%
                <span class="trend-label">vs last month</span>
              </div>
            </div>
            <div class="stat-icon" :style="{ background: stat.bgColor }">
              <el-icon :size="28" color="white">
                <component :is="stat.icon" />
              </el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Filters -->
    <el-card class="filter-card" shadow="hover">
      <div class="filter-container">
        <div class="filter-row">
          <el-input
              v-model="filters.keyword"
              placeholder="Search by title or description"
              prefix-icon="Search"
              clearable
              style="width: 240px"
              @clear="handleSearch"
              @keyup.enter="handleSearch"
          />
          <el-select v-model="filters.category" placeholder="Category" clearable style="width: 140px">
            <el-option label="Predictive Maintenance" value="Predictive Maintenance" />
            <el-option label="Energy Optimization" value="Energy Optimization" />
            <el-option label="Fault Detection" value="Fault Detection" />
            <el-option label="Cost Saving" value="Cost Saving" />
            <el-option label="ESG" value="ESG" />
          </el-select>
          <el-select v-model="filters.status" placeholder="Status" clearable style="width: 130px">
            <el-option label="New" value="New" />
            <el-option label="Under Review" value="Under Review" />
            <el-option label="Approved" value="Approved" />
            <el-option label="Implemented" value="Implemented" />
            <el-option label="Rejected" value="Rejected" />
          </el-select>
          <el-select v-model="filters.confidenceLevel" placeholder="Confidence" clearable style="width: 130px">
            <el-option label="High (≥80%)" value="High" />
            <el-option label="Medium (60-79%)" value="Medium" />
            <el-option label="Low (&lt;60%)" value="Low" />
          </el-select>
          <el-date-picker
              v-model="filters.dateRange"
              type="daterange"
              range-separator="to"
              start-placeholder="Start Date"
              end-placeholder="End Date"
              style="width: 260px"
          />
          <el-button type="primary" @click="handleSearch">Search</el-button>
          <el-button @click="handleResetFilters">Reset</el-button>
        </div>
      </div>
    </el-card>

    <!-- Main Table -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>AI Recommendations List</span>
          <div class="table-actions">
            <el-button :icon="Refresh" @click="fetchRecommendations" circle />
            <el-button :icon="Setting" @click="handleColumnSettings" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedRecommendations" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="title" label="Recommendation Title" min-width="200" show-overflow-tooltip />
        <el-table-column prop="category" label="Category" width="150">
          <template #default="{ row }">
            <el-tag :type="getCategoryTag(row.category)" size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="confidence" label="Confidence" width="130">
          <template #default="{ row }">
            <el-progress :percentage="row.confidence" :stroke-width="8" :color="getConfidenceColor(row.confidence)" />
          </template>
        </el-table-column>
        <el-table-column prop="impactScore" label="Impact Score" width="120">
          <template #default="{ row }">
            <div class="impact-score">
              <span class="score-value">{{ row.impactScore }}</span>
              <span class="score-max">/100</span>
              <el-rate v-model="row.impactScore" disabled :max="10" style="margin-left: 8px" />
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="estimatedSavings" label="Est. Savings (USD)" width="150">
          <template #default="{ row }">
            <span style="color: #67c23a; font-weight: 500">
              ${{ row.estimatedSavings.toLocaleString() }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="modelUsed" label="AI Model" width="140" show-overflow-tooltip />
        <el-table-column prop="generatedDate" label="Generated Date" width="110" />
        <el-table-column prop="decisionMaker" label="Decision Maker" width="120" />
        <el-table-column label="Actions" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDetail(row)">View</el-button>
            <el-button link type="success" size="small" @click="approveRecommendation(row)">Approve</el-button>
            <el-button link type="danger" size="small" @click="rejectRecommendation(row)">Reject</el-button>
            <el-button link type="warning" size="small" @click="implementRecommendation(row)">Implement</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredRecommendations.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- View/Edit Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogMode === 'view' ? 'AI Recommendation Details' : (dialogMode === 'approve' ? 'Approve Recommendation' : 'Implement Recommendation')" width="700px" destroy-on-close>
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="140px">
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="Recommendation Title">
              <el-input v-model="formData.title" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Category">
              <el-tag :type="getCategoryTag(formData.category)" size="default">{{ formData.category }}</el-tag>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Confidence">
              <el-progress :percentage="formData.confidence" :stroke-width="10" :color="getConfidenceColor(formData.confidence)" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Impact Score">
              <el-rate v-model="formData.impactScore" disabled :max="10" />
              <span style="margin-left: 8px">{{ formData.impactScore }}/10</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Est. Savings">
              <span style="color: #67c23a; font-weight: 500">${{ formData.estimatedSavings.toLocaleString() }}</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="AI Model">
              <el-input v-model="formData.modelUsed" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Generated Date">
              <el-input v-model="formData.generatedDate" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Decision Maker" v-if="dialogMode !== 'view'">
              <el-input v-model="formData.decisionMaker" placeholder="Enter decision maker name" />
            </el-form-item>
            <el-form-item label="Decision Maker" v-else>
              <el-input v-model="formData.decisionMaker" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="Description">
              <el-input v-model="formData.description" type="textarea" :rows="2" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="AI Reasoning" v-if="formData.aiReasoning">
              <el-input v-model="formData.aiReasoning" type="textarea" :rows="3" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="24" v-if="dialogMode !== 'view'">
            <el-form-item label="Implementation Notes" prop="implementationNotes">
              <el-input v-model="formData.implementationNotes" type="textarea" :rows="2" placeholder="Enter implementation notes or approval comments" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button v-if="dialogMode === 'approve'" type="success" @click="submitApproval">Confirm Approval</el-button>
        <el-button v-if="dialogMode === 'implement'" type="primary" @click="submitImplementation">Confirm Implementation</el-button>
      </template>
    </el-dialog>

    <!-- Run AI Analysis Dialog -->
    <el-dialog v-model="analysisDialogVisible" title="Run AI Analysis" width="500px">
      <el-form :model="analysisConfig" label-width="120px">
        <el-form-item label="Analysis Type">
          <el-select v-model="analysisConfig.type" style="width: 100%">
            <el-option label="Predictive Maintenance" value="Predictive Maintenance" />
            <el-option label="Energy Optimization" value="Energy Optimization" />
            <el-option label="Fault Detection" value="Fault Detection" />
            <el-option label="Cost Optimization" value="Cost Optimization" />
          </el-select>
        </el-form-item>
        <el-form-item label="Time Range">
          <el-date-picker v-model="analysisConfig.timeRange" type="daterange" range-separator="to" start-placeholder="Start" end-placeholder="End" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Data Sources">
          <el-checkbox-group v-model="analysisConfig.dataSources">
            <el-checkbox label="HVAC">HVAC</el-checkbox>
            <el-checkbox label="Electrical">Electrical</el-checkbox>
            <el-checkbox label="IoT Sensors">IoT Sensors</el-checkbox>
            <el-checkbox label="Historical Data">Historical Data</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="analysisDialogVisible = false">Cancel</el-button>
        <el-button type="primary" :loading="analysisRunning" @click="runAnalysis">Run Analysis</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  Plus, ArrowUp, ArrowDown, Document, Checked,
  Clock, TrendCharts, Refresh, Search, Download, Setting, Cpu
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading AI recommendations...',
  'Initializing ML models...',
  'Almost ready...'
]

// ==================== Interfaces ====================
interface AIRecommendation {
  id: number
  title: string
  category: string
  status: string
  confidence: number
  impactScore: number
  estimatedSavings: number
  modelUsed: string
  generatedDate: string
  decisionMaker: string
  description: string
  aiReasoning: string
  implementationNotes?: string
}

interface StatCard {
  title: string
  value: string | number
  trend: number
  icon: string
  bgColor: string
  key: string
}

// ==================== Chart References ====================
const confidenceChartRef = ref<HTMLElement>()
const categoryChartRef = ref<HTMLElement>()
let confidenceChart: echarts.ECharts | null = null
let categoryChart: echarts.ECharts | null = null

const confidencePeriod = ref<'weekly' | 'monthly'>('weekly')

// ==================== Mock Data ====================
const statsCards = ref<StatCard[]>([
  { title: 'Total Recommendations', value: 245, trend: 32, icon: 'Document', bgColor: '#409eff', key: 'total' },
  { title: 'Implemented', value: 98, trend: 28, icon: 'Checked', bgColor: '#67c23a', key: 'implemented' },
  { title: 'Avg. Confidence', value: '78%', trend: 5, icon: 'TrendCharts', bgColor: '#e6a23c', key: 'confidence' },
  { title: 'Est. Total Savings', value: '$3.2M', trend: 42, icon: 'Clock', bgColor: '#f56c6c', key: 'savings' }
])

const aiRecommendations = ref<AIRecommendation[]>([
  {
    id: 1,
    title: 'Chiller Bearing Failure Prediction',
    category: 'Predictive Maintenance',
    status: 'New',
    confidence: 92,
    impactScore: 9,
    estimatedSavings: 125000,
    modelUsed: 'LSTM Neural Network',
    generatedDate: '2024-01-18',
    decisionMaker: '',
    description: 'AI model predicts bearing failure in Chiller-02 within 30 days based on vibration pattern anomalies',
    aiReasoning: 'Vibration frequency increased by 23% over baseline. Thermal imaging shows abnormal temperature gradient. Similar pattern observed in historical failure cases.',
    implementationNotes: ''
  },
  {
    id: 2,
    title: 'HVAC Setpoint Optimization',
    category: 'Energy Optimization',
    status: 'Under Review',
    confidence: 85,
    impactScore: 8,
    estimatedSavings: 45000,
    modelUsed: 'Reinforcement Learning',
    generatedDate: '2024-01-17',
    decisionMaker: 'Sarah Chen',
    description: 'Dynamic setpoint adjustment based on occupancy and weather forecasts',
    aiReasoning: 'Reinforcement learning model optimized for 15% energy reduction. Weather forecast integration improves prediction accuracy.',
    implementationNotes: ''
  },
  {
    id: 3,
    title: 'Cooling Tower Fan Imbalance Detection',
    category: 'Fault Detection',
    status: 'New',
    confidence: 88,
    impactScore: 7,
    estimatedSavings: 28000,
    modelUsed: 'Random Forest',
    generatedDate: '2024-01-16',
    decisionMaker: '',
    description: 'Detected imbalance in CT-02 fan causing excessive vibration and energy waste',
    aiReasoning: 'Spectrum analysis shows 1X harmonic amplitude increase. Energy consumption 12% above expected baseline.',
    implementationNotes: ''
  },
  {
    id: 4,
    title: 'Peak Demand Reduction Strategy',
    category: 'Cost Saving',
    status: 'Approved',
    confidence: 79,
    impactScore: 9,
    estimatedSavings: 185000,
    modelUsed: 'Time Series Forecasting',
    generatedDate: '2024-01-15',
    decisionMaker: 'John Smith',
    description: 'Load shifting strategy to reduce peak demand charges by 25%',
    aiReasoning: 'Analysis of 24-month usage patterns identified optimal load shifting window. Peak demand predicted to exceed threshold 18 times this quarter.',
    implementationNotes: ''
  },
  {
    id: 5,
    title: 'AHU Filter Clogging Prediction',
    category: 'Predictive Maintenance',
    status: 'Implemented',
    confidence: 94,
    impactScore: 8,
    estimatedSavings: 32000,
    modelUsed: 'XGBoost',
    generatedDate: '2024-01-14',
    decisionMaker: 'Mike Johnson',
    description: 'Predictive filter replacement schedule based on pressure drop trends',
    aiReasoning: 'Pressure drop increase rate accelerated by 40%. Particle counter shows elevated PM2.5 levels.',
    implementationNotes: 'Filter replacement schedule optimized. Maintenance costs reduced by 30%.'
  },
  {
    id: 6,
    title: 'Lighting Schedule Optimization',
    category: 'Energy Optimization',
    status: 'Under Review',
    confidence: 82,
    impactScore: 6,
    estimatedSavings: 15000,
    modelUsed: 'Clustering Algorithm',
    generatedDate: '2024-01-13',
    decisionMaker: 'Lisa Zhang',
    description: 'Occupancy-based lighting control optimization',
    aiReasoning: 'Occupancy pattern analysis reveals 35% reduction opportunity during low-traffic periods.',
    implementationNotes: ''
  },
  {
    id: 7,
    title: 'UPS Battery Degradation Alert',
    category: 'Fault Detection',
    status: 'Rejected',
    confidence: 76,
    impactScore: 9,
    estimatedSavings: 75000,
    modelUsed: 'Anomaly Detection',
    generatedDate: '2024-01-12',
    decisionMaker: 'David Wang',
    description: 'Early warning for UPS battery capacity degradation',
    aiReasoning: 'Battery impedance increased by 35% over 60 days. Capacity test shows 25% reduction.',
    implementationNotes: 'Deferred to next maintenance cycle.'
  },
  {
    id: 8,
    title: 'VFD Energy Optimization',
    category: 'Energy Optimization',
    status: 'Implemented',
    confidence: 91,
    impactScore: 8,
    estimatedSavings: 68000,
    modelUsed: 'Genetic Algorithm',
    generatedDate: '2024-01-11',
    decisionMaker: 'Emily Zhao',
    description: 'Optimal VFD speed control based on real-time demand',
    aiReasoning: 'Speed setpoint optimization reduces energy use by 18% while maintaining system performance.',
    implementationNotes: 'VFD parameters updated. Energy monitoring shows 20% reduction achieved.'
  },
  {
    id: 9,
    title: 'Carbon Emission Reduction Opportunity',
    category: 'ESG',
    status: 'Approved',
    confidence: 73,
    impactScore: 10,
    estimatedSavings: 95000,
    modelUsed: 'Optimization Model',
    generatedDate: '2024-01-10',
    decisionMaker: 'James Wu',
    description: 'Renewable energy integration strategy to reduce Scope 2 emissions',
    aiReasoning: 'Solar generation forecast matches demand pattern with 65% correlation. Carbon offset potential of 120 tons annually.',
    implementationNotes: ''
  },
  {
    id: 10,
    title: 'Compressor Efficiency Degradation',
    category: 'Predictive Maintenance',
    status: 'New',
    confidence: 87,
    impactScore: 8,
    estimatedSavings: 42000,
    modelUsed: 'Isolation Forest',
    generatedDate: '2024-01-09',
    decisionMaker: '',
    description: 'Detected efficiency drop in air compressor system',
    aiReasoning: 'Power-to-air ratio increased by 12%. Leak detection algorithm identifies potential distribution leaks.',
    implementationNotes: ''
  },
  {
    id: 11,
    title: 'Thermal Comfort Optimization',
    category: 'Energy Optimization',
    status: 'Under Review',
    confidence: 70,
    impactScore: 7,
    estimatedSavings: 22000,
    modelUsed: 'Deep Q-Network',
    generatedDate: '2024-01-08',
    decisionMaker: 'Anna Kim',
    description: 'Balance energy efficiency with occupant comfort preferences',
    aiReasoning: 'Comfort-energy trade-off optimization yields 15% savings with minimal comfort impact.',
    implementationNotes: ''
  },
  {
    id: 12,
    title: 'Water Consumption Anomaly',
    category: 'Fault Detection',
    status: 'Implemented',
    confidence: 89,
    impactScore: 7,
    estimatedSavings: 18000,
    modelUsed: 'Statistical Process Control',
    generatedDate: '2024-01-07',
    decisionMaker: 'Robert Liu',
    description: 'Detected continuous water flow indicating potential leak',
    aiReasoning: 'Consumption pattern shows 24/7 baseline usage 40% above normal. Valve inspection confirmed slow leak.',
    implementationNotes: 'Leak repaired. Water consumption normalized.'
  }
])

// ==================== Reactive Variables ====================
const tableLoading = ref(false)
const dialogVisible = ref(false)
const analysisDialogVisible = ref(false)
const analysisRunning = ref(false)
const dialogMode = ref<'view' | 'approve' | 'implement'>('view')
const deleteTarget = ref<AIRecommendation | null>(null)
const formRef = ref()
const currentPage = ref(1)
const pageSize = ref(10)

const filters = reactive({
  keyword: '',
  category: '',
  status: '',
  confidenceLevel: '',
  dateRange: null as [Date, Date] | null
})

const analysisConfig = reactive({
  type: 'Predictive Maintenance',
  timeRange: null as [Date, Date] | null,
  dataSources: ['HVAC', 'Electrical', 'IoT Sensors', 'Historical Data']
})

const formData = reactive<AIRecommendation>({
  id: 0,
  title: '',
  category: '',
  status: '',
  confidence: 0,
  impactScore: 0,
  estimatedSavings: 0,
  modelUsed: '',
  generatedDate: '',
  decisionMaker: '',
  description: '',
  aiReasoning: '',
  implementationNotes: ''
})

const formRules = {
  decisionMaker: [{ required: true, message: 'Please enter decision maker name', trigger: 'blur' }]
}

// ==================== Computed ====================
const filteredRecommendations = computed(() => {
  let filtered = [...aiRecommendations.value]

  if (filters.keyword) {
    filtered = filtered.filter(r =>
        r.title.toLowerCase().includes(filters.keyword.toLowerCase()) ||
        r.description.toLowerCase().includes(filters.keyword.toLowerCase())
    )
  }

  if (filters.category) {
    filtered = filtered.filter(r => r.category === filters.category)
  }

  if (filters.status) {
    filtered = filtered.filter(r => r.status === filters.status)
  }

  if (filters.confidenceLevel) {
    filtered = filtered.filter(r => {
      if (filters.confidenceLevel === 'High') return r.confidence >= 80
      if (filters.confidenceLevel === 'Medium') return r.confidence >= 60 && r.confidence < 80
      if (filters.confidenceLevel === 'Low') return r.confidence < 60
      return true
    })
  }

  if (filters.dateRange && filters.dateRange[0] && filters.dateRange[1]) {
    filtered = filtered.filter(r => {
      const date = new Date(r.generatedDate)
      return date >= filters.dateRange![0] && date <= filters.dateRange![1]
    })
  }

  return filtered
})

const paginatedRecommendations = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredRecommendations.value.slice(start, end)
})

// ==================== Helper Methods ====================
const getCategoryTag = (category: string): string => {
  const map: Record<string, string> = {
    'Predictive Maintenance': 'primary',
    'Energy Optimization': 'success',
    'Fault Detection': 'warning',
    'Cost Saving': 'info',
    'ESG': 'success'
  }
  return map[category] || 'info'
}

const getStatusTag = (status: string): string => {
  const map: Record<string, string> = {
    'New': 'info',
    'Under Review': 'warning',
    'Approved': 'primary',
    'Implemented': 'success',
    'Rejected': 'danger'
  }
  return map[status] || 'info'
}

const getConfidenceColor = (confidence: number): string => {
  if (confidence >= 80) return '#67c23a'
  if (confidence >= 60) return '#e6a23c'
  return '#f56c6c'
}

// ==================== Chart Initialization ====================
const initConfidenceChart = () => {
  if (!confidenceChartRef.value) return
  if (confidenceChart) confidenceChart.dispose()

  confidenceChart = echarts.init(confidenceChartRef.value)
  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['Average Confidence (%)', 'Number of Recommendations'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '12%', containLabel: true },
    xAxis: { type: 'category', data: ['Week 1', 'Week 2', 'Week 3', 'Week 4'] },
    yAxis: [{ type: 'value', name: 'Confidence (%)', min: 0, max: 100 }, { type: 'value', name: 'Count' }],
    series: [
      { name: 'Average Confidence (%)', type: 'line', data: [72, 74, 76, 78], smooth: true, lineStyle: { width: 3, color: '#409eff' }, symbolSize: 8, yAxisIndex: 0 },
      { name: 'Number of Recommendations', type: 'bar', data: [18, 22, 25, 30], yAxisIndex: 1, itemStyle: { borderRadius: [4, 4, 0, 0], color: '#67c23a' } }
    ]
  }
  confidenceChart.setOption(option)
  window.addEventListener('resize', () => confidenceChart?.resize())
}

const initCategoryChart = () => {
  if (!categoryChartRef.value) return
  if (categoryChart) categoryChart.dispose()

  categoryChart = echarts.init(categoryChartRef.value)
  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [
      {
        name: 'Recommendations by Category',
        type: 'pie',
        radius: '55%',
        data: [
          { value: 42, name: 'Predictive Maintenance', itemStyle: { color: '#409eff' } },
          { value: 28, name: 'Energy Optimization', itemStyle: { color: '#67c23a' } },
          { value: 18, name: 'Fault Detection', itemStyle: { color: '#e6a23c' } },
          { value: 8, name: 'Cost Saving', itemStyle: { color: '#f56c6c' } },
          { value: 4, name: 'ESG', itemStyle: { color: '#909399' } }
        ],
        emphasis: { scale: true },
        label: { show: true, formatter: '{b}: {d}%' }
      }
    ]
  }
  categoryChart.setOption(option)
  window.addEventListener('resize', () => categoryChart?.resize())
}

// ==================== Interactive Methods ====================
const handleCardClick = (stat: StatCard) => {
  ElMessage.info(`Viewing ${stat.title} details`)
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleResetFilters = () => {
  filters.keyword = ''
  filters.category = ''
  filters.status = ''
  filters.confidenceLevel = ''
  filters.dateRange = null
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

const handleExport = () => {
  ElMessage.success(`Exporting ${filteredRecommendations.value.length} AI recommendations...`)
}

const handleColumnSettings = () => {
  ElMessage.info('Column settings dialog would open here')
}

const fetchRecommendations = () => {
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
    ElMessage.success('Data refreshed')
  }, 500)
}

const handleRunAIAnalysis = () => {
  analysisDialogVisible.value = true
}

const runAnalysis = () => {
  analysisRunning.value = true
  setTimeout(() => {
    analysisRunning.value = false
    analysisDialogVisible.value = false
    ElMessage.success('AI analysis completed. 3 new recommendations generated.')
    // Simulate adding new recommendations
    const newRecommendations = [
      {
        id: Date.now(),
        title: `${analysisConfig.type} Analysis Result`,
        category: analysisConfig.type,
        status: 'New',
        confidence: Math.floor(Math.random() * 30) + 65,
        impactScore: Math.floor(Math.random() * 5) + 5,
        estimatedSavings: Math.floor(Math.random() * 100000) + 10000,
        modelUsed: 'AI Model',
        generatedDate: new Date().toISOString().split('T')[0],
        decisionMaker: '',
        description: `AI-generated recommendation based on ${analysisConfig.type} analysis`,
        aiReasoning: 'Analysis complete. Multiple patterns detected.',
        implementationNotes: ''
      }
    ]
    aiRecommendations.value.unshift(...newRecommendations)
  }, 2000)
}

const viewDetail = (row: AIRecommendation) => {
  dialogMode.value = 'view'
  Object.assign(formData, row)
  dialogVisible.value = true
}

const approveRecommendation = (row: AIRecommendation) => {
  dialogMode.value = 'approve'
  Object.assign(formData, row)
  formData.decisionMaker = ''
  formData.implementationNotes = ''
  dialogVisible.value = true
}

const rejectRecommendation = (row: AIRecommendation) => {
  ElMessageBox.confirm(`Reject recommendation "${row.title}"?`, 'Reject Confirmation', {
    confirmButtonText: 'Reject',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    const index = aiRecommendations.value.findIndex(r => r.id === row.id)
    if (index !== -1) {
      aiRecommendations.value[index].status = 'Rejected'
      ElMessage.warning(`Rejected: ${row.title}`)
    }
  }).catch(() => {})
}

const implementRecommendation = (row: AIRecommendation) => {
  dialogMode.value = 'implement'
  Object.assign(formData, row)
  formData.decisionMaker = ''
  formData.implementationNotes = ''
  dialogVisible.value = true
}

const submitApproval = async () => {
  if (!formRef.value) return
  await formRef.value.validate((valid: boolean) => {
    if (valid) {
      const index = aiRecommendations.value.findIndex(r => r.id === formData.id)
      if (index !== -1) {
        aiRecommendations.value[index].status = 'Approved'
        aiRecommendations.value[index].decisionMaker = formData.decisionMaker
        aiRecommendations.value[index].implementationNotes = formData.implementationNotes
        ElMessage.success(`Approved: ${formData.title}`)
      }
      dialogVisible.value = false
    }
  })
}

const submitImplementation = async () => {
  if (!formRef.value) return
  await formRef.value.validate((valid: boolean) => {
    if (valid) {
      const index = aiRecommendations.value.findIndex(r => r.id === formData.id)
      if (index !== -1) {
        aiRecommendations.value[index].status = 'Implemented'
        aiRecommendations.value[index].decisionMaker = formData.decisionMaker
        aiRecommendations.value[index].implementationNotes = formData.implementationNotes
        ElMessage.success(`Implemented: ${formData.title}`)
      }
      dialogVisible.value = false
    }
  })
}

const handleSizeChange = () => {
  currentPage.value = 1
}

const handleCurrentChange = () => {}

// ==================== Loading Simulation ====================
const initCharts = async () => {
  await nextTick()
  setTimeout(() => {
    initConfidenceChart()
    initCategoryChart()
  }, 100)
}

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
      initCharts()
      fetchRecommendations()
    }, 400)
  }, 2000)
})
</script>

<style scoped lang="scss">
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

.spinner-ring:nth-child(1) {
  border-top-color: #3b82f6;
  animation-delay: 0s;
}

.spinner-ring:nth-child(2) {
  border-right-color: #f59e0b;
  animation-delay: 0.2s;
  width: 70%;
  height: 70%;
  top: 15%;
  left: 15%;
}

.spinner-ring:nth-child(3) {
  border-bottom-color: #10b981;
  animation-delay: 0.4s;
  width: 40%;
  height: 40%;
  top: 30%;
  left: 30%;
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

/* ==================== Main Page Styles ==================== */
.ai-recommendations-page {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;

  .breadcrumb {
    margin-bottom: 8px;
  }

  h1 {
    font-size: 28px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 8px 0;
  }

  .description {
    color: #909399;
    font-size: 14px;
    margin: 0;
  }

  .header-actions {
    display: flex;
    gap: 12px;
  }
}

.stats-row {
  margin-bottom: 20px;
}

.chart-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }
}

.chart-container {
  width: 100%;
  height: 320px;
}

.chart-container-small {
  width: 100%;
  height: 320px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    transform: translateY(-4px);
  }

  .stat-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .stat-info {
    flex: 1;
  }

  .stat-title {
    font-size: 14px;
    color: #909399;
    margin-bottom: 8px;
  }

  .stat-value {
    font-size: 28px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 8px;
  }

  .stat-trend {
    font-size: 12px;
    display: flex;
    align-items: center;
    gap: 4px;

    &.up { color: #67c23a; }
    &.down { color: #f56c6c; }

    .trend-label {
      color: #909399;
      margin-left: 4px;
    }
  }

  .stat-icon {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.filter-card {
  margin-bottom: 20px;

  .filter-container {
    .filter-row {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
    }
  }
}

.table-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }

  .table-actions {
    display: flex;
    gap: 8px;
    align-items: center;
  }
}

.impact-score {
  display: flex;
  align-items: center;

  .score-value {
    font-weight: 600;
    font-size: 14px;
  }

  .score-max {
    font-size: 12px;
    color: #909399;
    margin-left: 2px;
  }
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

:deep(.el-table) {
  font-size: 13px;
}

:deep(.el-dialog__body) {
  padding-top: 20px;
  max-height: 60vh;
  overflow-y: auto;
}

:deep(.el-rate) {
  display: inline-flex;
}
</style>