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
        <div class="loading-tip">Energy Decisions Register</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="energy-decisions-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Decision & Evidence</el-breadcrumb-item>
            <el-breadcrumb-item>Decision Register</el-breadcrumb-item>
            <el-breadcrumb-item>Energy Decisions</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Energy Decisions</h1>
        <p class="description">Track and manage energy optimization initiatives, efficiency projects, and consumption reduction strategies</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export
        </el-button>
        <el-button type="primary" @click="handleCreateDecision">
          <el-icon><Plus /></el-icon>
          New Energy Decision
        </el-button>
      </div>
    </div>

    <!-- Energy Overview Charts -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :lg="14">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Energy Savings Trend (kWh)</span>
              <el-radio-group v-model="savingsPeriod" size="small">
                <el-radio-button value="monthly">Monthly</el-radio-button>
                <el-radio-button value="quarterly">Quarterly</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="savingsChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="10">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Savings by Category</span>
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
                <span class="trend-label">vs last quarter</span>
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
          <el-select v-model="filters.category" placeholder="Energy Category" clearable style="width: 160px">
            <el-option label="HVAC" value="HVAC" />
            <el-option label="Lighting" value="Lighting" />
            <el-option label="Power" value="Power" />
            <el-option label="Renewable" value="Renewable" />
            <el-option label="Building Envelope" value="Building Envelope" />
          </el-select>
          <el-select v-model="filters.status" placeholder="Status" clearable style="width: 130px">
            <el-option label="Proposed" value="Proposed" />
            <el-option label="Approved" value="Approved" />
            <el-option label="In Progress" value="In Progress" />
            <el-option label="Completed" value="Completed" />
            <el-option label="Cancelled" value="Cancelled" />
          </el-select>
          <el-select v-model="filters.implementationPhase" placeholder="Phase" clearable style="width: 130px">
            <el-option label="Planning" value="Planning" />
            <el-option label="Design" value="Design" />
            <el-option label="Procurement" value="Procurement" />
            <el-option label="Installation" value="Installation" />
            <el-option label="Commissioning" value="Commissioning" />
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
          <span>Energy Decisions List</span>
          <div class="table-actions">
            <el-button :icon="Refresh" @click="fetchDecisions" circle />
            <el-button :icon="Setting" @click="handleColumnSettings" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedDecisions" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="title" label="Decision Title" min-width="200" show-overflow-tooltip />
        <el-table-column prop="category" label="Category" width="130">
          <template #default="{ row }">
            <el-tag :type="getCategoryTag(row.category)" size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="implementationPhase" label="Phase" width="120">
          <template #default="{ row }">
            <el-tag :type="getPhaseTag(row.implementationPhase)" size="small">{{ row.implementationPhase }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="annualSavings" label="Annual Savings (kWh)" width="150">
          <template #default="{ row }">
            <span style="color: #67c23a; font-weight: 500">
              {{ row.annualSavings.toLocaleString() }} kWh
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="investment" label="Investment (USD)" width="130">
          <template #default="{ row }">
            ${{ row.investment.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="paybackPeriod" label="Payback Period" width="110">
          <template #default="{ row }">
            <span :style="{ color: row.paybackPeriod <= 2 ? '#67c23a' : row.paybackPeriod <= 5 ? '#e6a23c' : '#f56c6c' }">
              {{ row.paybackPeriod }} years
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="roi" label="ROI" width="90">
          <template #default="{ row }">
            <span style="color: #67c23a">{{ row.roi }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="co2Reduction" label="CO₂ Reduction (t)" width="130">
          <template #default="{ row }">
            {{ row.co2Reduction.toLocaleString() }} t
          </template>
        </el-table-column>
        <el-table-column prop="decisionMaker" label="Decision Maker" width="120" />
        <el-table-column prop="decisionDate" label="Decision Date" width="110" />
        <el-table-column label="Actions" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDetail(row)">View</el-button>
            <el-button link type="success" size="small" @click="editDecision(row)">Edit</el-button>
            <el-button link type="danger" size="small" @click="deleteDecision(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredDecisions.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- View/Edit Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogMode === 'create' ? 'New Energy Decision' : (dialogMode === 'edit' ? 'Edit Energy Decision' : 'Energy Decision Details')" width="800px" destroy-on-close>
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="140px" :disabled="dialogMode === 'view'">
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="Decision Title" prop="title">
              <el-input v-model="formData.title" placeholder="Enter decision title" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Energy Category" prop="category">
              <el-select v-model="formData.category" placeholder="Select category" style="width: 100%">
                <el-option label="HVAC" value="HVAC" />
                <el-option label="Lighting" value="Lighting" />
                <el-option label="Power" value="Power" />
                <el-option label="Renewable" value="Renewable" />
                <el-option label="Building Envelope" value="Building Envelope" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Status" prop="status">
              <el-select v-model="formData.status" placeholder="Select status" style="width: 100%">
                <el-option label="Proposed" value="Proposed" />
                <el-option label="Approved" value="Approved" />
                <el-option label="In Progress" value="In Progress" />
                <el-option label="Completed" value="Completed" />
                <el-option label="Cancelled" value="Cancelled" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Implementation Phase" prop="implementationPhase">
              <el-select v-model="formData.implementationPhase" placeholder="Select phase" style="width: 100%">
                <el-option label="Planning" value="Planning" />
                <el-option label="Design" value="Design" />
                <el-option label="Procurement" value="Procurement" />
                <el-option label="Installation" value="Installation" />
                <el-option label="Commissioning" value="Commissioning" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Decision Maker" prop="decisionMaker">
              <el-input v-model="formData.decisionMaker" placeholder="Enter decision maker" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Decision Date" prop="decisionDate">
              <el-date-picker v-model="formData.decisionDate" type="date" placeholder="Select date" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Annual Savings (kWh)" prop="annualSavings">
              <el-input-number v-model="formData.annualSavings" :min="0" :step="10000" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Investment (USD)" prop="investment">
              <el-input-number v-model="formData.investment" :min="0" :step="5000" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Payback Period (years)" prop="paybackPeriod">
              <el-input-number v-model="formData.paybackPeriod" :min="0" :step="0.5" :precision="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="ROI (%)" prop="roi">
              <el-input-number v-model="formData.roi" :min="-20" :max="200" :step="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="CO₂ Reduction (t)" prop="co2Reduction">
              <el-input-number v-model="formData.co2Reduction" :min="0" :step="100" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="GHG Scope" prop="scope">
              <el-select v-model="formData.scope" placeholder="Select GHG scope" style="width: 100%">
                <el-option label="Scope 1" value="Scope 1" />
                <el-option label="Scope 2" value="Scope 2" />
                <el-option label="Scope 3" value="Scope 3" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="Description" prop="description">
              <el-input v-model="formData.description" type="textarea" :rows="2" placeholder="Enter decision description" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="Expected Outcomes" prop="expectedOutcomes">
              <el-input v-model="formData.expectedOutcomes" type="textarea" :rows="2" placeholder="Enter expected outcomes" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Close</el-button>
        <el-button v-if="dialogMode !== 'view'" type="primary" @click="submitForm">Submit</el-button>
      </template>
    </el-dialog>

    <!-- Delete Confirmation Dialog -->
    <el-dialog v-model="deleteDialogVisible" title="Confirm Delete" width="400px">
      <p>Are you sure you want to delete energy decision "{{ deleteTarget?.title }}"?</p>
      <p style="color: #f56c6c; font-size: 12px; margin-top: 8px">This action cannot be undone.</p>
      <template #footer>
        <el-button @click="deleteDialogVisible = false">Cancel</el-button>
        <el-button type="danger" @click="confirmDelete">Delete</el-button>
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
  Clock, TrendCharts, Refresh, Search, Download, Setting
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading energy decisions...',
  'Calculating savings data...',
  'Almost ready...'
]

// ==================== Interfaces ====================
interface EnergyDecision {
  id: number
  title: string
  category: string
  status: string
  implementationPhase: string
  annualSavings: number
  investment: number
  paybackPeriod: number
  roi: number
  co2Reduction: number
  scope: string
  decisionMaker: string
  decisionDate: string
  description: string
  expectedOutcomes: string
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
const savingsChartRef = ref<HTMLElement>()
const categoryChartRef = ref<HTMLElement>()
let savingsChart: echarts.ECharts | null = null
let categoryChart: echarts.ECharts | null = null

const savingsPeriod = ref<'monthly' | 'quarterly'>('monthly')

// ==================== Mock Data ====================
const statsCards = ref<StatCard[]>([
  { title: 'Total Decisions', value: 94, trend: 15, icon: 'Document', bgColor: '#409eff', key: 'total' },
  { title: 'Total Annual Savings', value: '8.45M kWh', trend: 22, icon: 'TrendCharts', bgColor: '#67c23a', key: 'savings' },
  { title: 'Total Investment', value: '$5.2M', trend: 18, icon: 'Clock', bgColor: '#e6a23c', key: 'investment' },
  { title: 'CO₂ Reduction', value: '3,280 t', trend: 28, icon: 'Checked', bgColor: '#f56c6c', key: 'carbon' }
])

const energyDecisions = ref<EnergyDecision[]>([
  {
    id: 1,
    title: 'LED Lighting Retrofit - Building A',
    category: 'Lighting',
    status: 'Completed',
    implementationPhase: 'Commissioning',
    annualSavings: 185000,
    investment: 125000,
    paybackPeriod: 2.5,
    roi: 40,
    co2Reduction: 78,
    scope: 'Scope 2',
    decisionMaker: 'John Smith',
    decisionDate: '2024-01-05',
    description: 'Replace all fluorescent lighting with LED fixtures',
    expectedOutcomes: '40% reduction in lighting energy consumption'
  },
  {
    id: 2,
    title: 'HVAC Variable Frequency Drive Installation',
    category: 'HVAC',
    status: 'In Progress',
    implementationPhase: 'Installation',
    annualSavings: 320000,
    investment: 280000,
    paybackPeriod: 3.2,
    roi: 31,
    co2Reduction: 145,
    scope: 'Scope 2',
    decisionMaker: 'Sarah Chen',
    decisionDate: '2024-01-10',
    description: 'Install VFDs on all AHU fans and pumps',
    expectedOutcomes: '35% reduction in HVAC energy use'
  },
  {
    id: 3,
    title: 'Solar Panel Installation - Phase 1',
    category: 'Renewable',
    status: 'Approved',
    implementationPhase: 'Procurement',
    annualSavings: 425000,
    investment: 850000,
    paybackPeriod: 5.5,
    roi: 18,
    co2Reduction: 195,
    scope: 'Scope 2',
    decisionMaker: 'David Wang',
    decisionDate: '2024-01-15',
    description: 'Install 500kW solar PV system on roof',
    expectedOutcomes: '20% of building electricity from renewable sources'
  },
  {
    id: 4,
    title: 'Building Automation System Upgrade',
    category: 'HVAC',
    status: 'Completed',
    implementationPhase: 'Commissioning',
    annualSavings: 215000,
    investment: 195000,
    paybackPeriod: 3.0,
    roi: 33,
    co2Reduction: 98,
    scope: 'Scope 2',
    decisionMaker: 'Lisa Zhang',
    decisionDate: '2023-12-20',
    description: 'Upgrade BMS with predictive controls',
    expectedOutcomes: 'Optimized HVAC scheduling and setpoints'
  },
  {
    id: 5,
    title: 'Chiller Plant Optimization',
    category: 'HVAC',
    status: 'In Progress',
    implementationPhase: 'Installation',
    annualSavings: 280000,
    investment: 350000,
    paybackPeriod: 4.0,
    roi: 25,
    co2Reduction: 128,
    scope: 'Scope 2',
    decisionMaker: 'Mike Johnson',
    decisionDate: '2024-01-08',
    description: 'Install high-efficiency chillers and controls',
    expectedOutcomes: '30% improvement in chiller efficiency'
  },
  {
    id: 6,
    title: 'Window Film Installation',
    category: 'Building Envelope',
    status: 'Completed',
    implementationPhase: 'Commissioning',
    annualSavings: 45000,
    investment: 32000,
    paybackPeriod: 2.1,
    roi: 48,
    co2Reduction: 20,
    scope: 'Scope 2',
    decisionMaker: 'Emily Zhao',
    decisionDate: '2023-12-15',
    description: 'Install solar control film on south-facing windows',
    expectedOutcomes: 'Reduced cooling load by 15%'
  },
  {
    id: 7,
    title: 'Electric Vehicle Charging Stations',
    category: 'Power',
    status: 'Approved',
    implementationPhase: 'Design',
    annualSavings: 0,
    investment: 75000,
    paybackPeriod: 0,
    roi: -15,
    co2Reduction: 45,
    scope: 'Scope 3',
    decisionMaker: 'Tom Harris',
    decisionDate: '2024-01-12',
    description: 'Install 10 EV charging stations in parking garage',
    expectedOutcomes: 'Support employee EV adoption, reduce fleet emissions'
  },
  {
    id: 8,
    title: 'Compressed Air System Leak Repair',
    category: 'Power',
    status: 'Completed',
    implementationPhase: 'Commissioning',
    annualSavings: 65000,
    investment: 15000,
    paybackPeriod: 0.7,
    roi: 143,
    co2Reduction: 30,
    scope: 'Scope 2',
    decisionMaker: 'Robert Liu',
    decisionDate: '2024-01-03',
    description: 'Identify and repair compressed air leaks',
    expectedOutcomes: '25% reduction in compressed air energy use'
  },
  {
    id: 9,
    title: 'Energy Storage System Installation',
    category: 'Power',
    status: 'Proposed',
    implementationPhase: 'Planning',
    annualSavings: 95000,
    investment: 420000,
    paybackPeriod: 7.0,
    roi: 14,
    co2Reduction: 52,
    scope: 'Scope 2',
    decisionMaker: 'James Wu',
    decisionDate: '2024-01-18',
    description: 'Install battery storage for peak shaving',
    expectedOutcomes: 'Reduce peak demand charges by 30%'
  },
  {
    id: 10,
    title: 'Smart Thermostat Deployment',
    category: 'HVAC',
    status: 'In Progress',
    implementationPhase: 'Installation',
    annualSavings: 35000,
    investment: 28000,
    paybackPeriod: 2.3,
    roi: 43,
    co2Reduction: 16,
    scope: 'Scope 2',
    decisionMaker: 'Anna Kim',
    decisionDate: '2024-01-14',
    description: 'Install smart thermostats in all offices',
    expectedOutcomes: '20% reduction in HVAC runtime'
  },
  {
    id: 11,
    title: 'Daylight Harvesting System',
    category: 'Lighting',
    status: 'Approved',
    implementationPhase: 'Procurement',
    annualSavings: 28000,
    investment: 45000,
    paybackPeriod: 4.8,
    roi: 21,
    co2Reduction: 13,
    scope: 'Scope 2',
    decisionMaker: 'John Smith',
    decisionDate: '2024-01-16',
    description: 'Install daylight sensors and dimming controls',
    expectedOutcomes: 'Adjust artificial lighting based on natural light'
  },
  {
    id: 12,
    title: 'Green Roof Installation',
    category: 'Building Envelope',
    status: 'Proposed',
    implementationPhase: 'Planning',
    annualSavings: 15000,
    investment: 180000,
    paybackPeriod: 12.0,
    roi: 8,
    co2Reduction: 25,
    scope: 'Scope 2',
    decisionMaker: 'Sarah Chen',
    decisionDate: '2024-01-20',
    description: 'Install green roof on Building C',
    expectedOutcomes: 'Improved insulation and stormwater management'
  }
])

// ==================== Reactive Variables ====================
const tableLoading = ref(false)
const dialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit' | 'view'>('view')
const deleteTarget = ref<EnergyDecision | null>(null)
const formRef = ref()
const currentPage = ref(1)
const pageSize = ref(10)

const filters = reactive({
  keyword: '',
  category: '',
  status: '',
  implementationPhase: '',
  dateRange: null as [Date, Date] | null
})

const formData = reactive<EnergyDecision>({
  id: 0,
  title: '',
  category: 'HVAC',
  status: 'Proposed',
  implementationPhase: 'Planning',
  annualSavings: 0,
  investment: 0,
  paybackPeriod: 0,
  roi: 0,
  co2Reduction: 0,
  scope: 'Scope 2',
  decisionMaker: '',
  decisionDate: '',
  description: '',
  expectedOutcomes: ''
})

const formRules = {
  title: [{ required: true, message: 'Please enter decision title', trigger: 'blur' }],
  category: [{ required: true, message: 'Please select energy category', trigger: 'change' }],
  status: [{ required: true, message: 'Please select status', trigger: 'change' }],
  annualSavings: [{ required: true, message: 'Please enter annual savings', trigger: 'blur' }],
  investment: [{ required: true, message: 'Please enter investment amount', trigger: 'blur' }],
  decisionMaker: [{ required: true, message: 'Please enter decision maker', trigger: 'blur' }]
}

// ==================== Computed ====================
const filteredDecisions = computed(() => {
  let filtered = [...energyDecisions.value]

  if (filters.keyword) {
    filtered = filtered.filter(d =>
        d.title.toLowerCase().includes(filters.keyword.toLowerCase()) ||
        d.description.toLowerCase().includes(filters.keyword.toLowerCase()) ||
        d.expectedOutcomes.toLowerCase().includes(filters.keyword.toLowerCase())
    )
  }

  if (filters.category) {
    filtered = filtered.filter(d => d.category === filters.category)
  }

  if (filters.status) {
    filtered = filtered.filter(d => d.status === filters.status)
  }

  if (filters.implementationPhase) {
    filtered = filtered.filter(d => d.implementationPhase === filters.implementationPhase)
  }

  if (filters.dateRange && filters.dateRange[0] && filters.dateRange[1]) {
    filtered = filtered.filter(d => {
      const date = new Date(d.decisionDate)
      return date >= filters.dateRange![0] && date <= filters.dateRange![1]
    })
  }

  return filtered
})

const paginatedDecisions = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredDecisions.value.slice(start, end)
})

// ==================== Helper Methods ====================
const getCategoryTag = (category: string): string => {
  const map: Record<string, string> = {
    'HVAC': 'primary',
    'Lighting': 'success',
    'Power': 'warning',
    'Renewable': 'success',
    'Building Envelope': 'info'
  }
  return map[category] || 'info'
}

const getStatusTag = (status: string): string => {
  const map: Record<string, string> = {
    'Proposed': 'info',
    'Approved': 'primary',
    'In Progress': 'warning',
    'Completed': 'success',
    'Cancelled': 'danger'
  }
  return map[status] || 'info'
}

const getPhaseTag = (phase: string): string => {
  const map: Record<string, string> = {
    'Planning': 'info',
    'Design': 'primary',
    'Procurement': 'warning',
    'Installation': 'warning',
    'Commissioning': 'success'
  }
  return map[phase] || 'info'
}

// ==================== Chart Initialization ====================
const initSavingsChart = () => {
  if (!savingsChartRef.value) return
  if (savingsChart) savingsChart.dispose()

  savingsChart = echarts.init(savingsChartRef.value)
  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['Actual Savings', 'Target Savings'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '12%', containLabel: true },
    xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] },
    yAxis: { type: 'value', name: 'Savings (kWh)' },
    series: [
      { name: 'Actual Savings', type: 'line', data: [12500, 14800, 16200, 18500, 19800, 21200, 23500, 24800, 26200, 28500, 29800, 31200], smooth: true, lineStyle: { width: 3, color: '#67c23a' }, symbolSize: 8, areaStyle: { opacity: 0.1 } },
      { name: 'Target Savings', type: 'line', data: [15000, 15500, 16000, 17500, 18500, 20000, 22000, 23000, 24500, 26000, 27500, 29000], lineStyle: { width: 2, color: '#909399', type: 'dashed' }, symbolSize: 6 }
    ]
  }
  savingsChart.setOption(option)
  window.addEventListener('resize', () => savingsChart?.resize())
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
        name: 'Savings by Category',
        type: 'pie',
        radius: '55%',
        data: [
          { value: 42, name: 'HVAC', itemStyle: { color: '#409eff' } },
          { value: 23, name: 'Lighting', itemStyle: { color: '#67c23a' } },
          { value: 18, name: 'Power', itemStyle: { color: '#e6a23c' } },
          { value: 12, name: 'Renewable', itemStyle: { color: '#f56c6c' } },
          { value: 5, name: 'Building Envelope', itemStyle: { color: '#909399' } }
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
  filters.implementationPhase = ''
  filters.dateRange = null
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

const handleExport = () => {
  ElMessage.success(`Exporting ${filteredDecisions.value.length} energy decisions...`)
}

const handleColumnSettings = () => {
  ElMessage.info('Column settings dialog would open here')
}

const fetchDecisions = () => {
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
    ElMessage.success('Data refreshed')
  }, 500)
}

const handleCreateDecision = () => {
  dialogMode.value = 'create'
  Object.assign(formData, {
    id: Date.now(),
    title: '',
    category: 'HVAC',
    status: 'Proposed',
    implementationPhase: 'Planning',
    annualSavings: 0,
    investment: 0,
    paybackPeriod: 0,
    roi: 0,
    co2Reduction: 0,
    scope: 'Scope 2',
    decisionMaker: '',
    decisionDate: new Date().toISOString().split('T')[0],
    description: '',
    expectedOutcomes: ''
  })
  dialogVisible.value = true
}

const viewDetail = (row: EnergyDecision) => {
  dialogMode.value = 'view'
  Object.assign(formData, row)
  dialogVisible.value = true
}

const editDecision = (row: EnergyDecision) => {
  dialogMode.value = 'edit'
  Object.assign(formData, row)
  dialogVisible.value = true
}

const deleteDecision = (row: EnergyDecision) => {
  deleteTarget.value = row
  deleteDialogVisible.value = true
}

const confirmDelete = () => {
  if (deleteTarget.value) {
    const index = energyDecisions.value.findIndex(d => d.id === deleteTarget.value!.id)
    if (index !== -1) {
      energyDecisions.value.splice(index, 1)
      ElMessage.success(`Deleted: ${deleteTarget.value.title}`)
    }
  }
  deleteDialogVisible.value = false
  deleteTarget.value = null
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate((valid: boolean) => {
    if (valid) {
      if (dialogMode.value === 'create') {
        energyDecisions.value.unshift({ ...formData, id: Date.now() })
        ElMessage.success('Energy decision created successfully')
      } else if (dialogMode.value === 'edit') {
        const index = energyDecisions.value.findIndex(d => d.id === formData.id)
        if (index !== -1) {
          energyDecisions.value[index] = { ...formData }
          ElMessage.success('Energy decision updated successfully')
        }
      }
      dialogVisible.value = false
      currentPage.value = 1
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
    initSavingsChart()
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
      fetchDecisions()
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
.energy-decisions-page {
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
</style>