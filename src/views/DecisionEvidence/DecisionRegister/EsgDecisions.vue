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
        <div class="loading-tip">ESG Decisions Register</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="esg-decisions-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Decision & Evidence</el-breadcrumb-item>
            <el-breadcrumb-item>Decision Register</el-breadcrumb-item>
            <el-breadcrumb-item>ESG Decisions</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>ESG Decisions</h1>
        <p class="description">Manage environmental, social, and governance decisions with compliance tracking and impact assessment</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export
        </el-button>
        <el-button type="primary" @click="handleCreateDecision">
          <el-icon><Plus /></el-icon>
          New ESG Decision
        </el-button>
      </div>
    </div>

    <!-- ESG Score Overview -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :lg="16">
        <el-card class="esg-score-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>ESG Performance Score</span>
              <el-radio-group v-model="esgTimeRange" size="small">
                <el-radio-button value="quarter">Quarter</el-radio-button>
                <el-radio-button value="year">Year</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="esgChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="8">
        <el-card class="stats-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>ESG Pillar Breakdown</span>
            </div>
          </template>
          <div ref="pillarChartRef" class="chart-container-small"></div>
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
              style="width: 260px"
              @clear="handleSearch"
              @keyup.enter="handleSearch"
          />
          <el-select v-model="filters.pillar" placeholder="ESG Pillar" clearable style="width: 140px">
            <el-option label="Environmental" value="Environmental" />
            <el-option label="Social" value="Social" />
            <el-option label="Governance" value="Governance" />
          </el-select>
          <el-select v-model="filters.status" placeholder="Status" clearable style="width: 140px">
            <el-option label="Draft" value="Draft" />
            <el-option label="In Review" value="In Review" />
            <el-option label="Approved" value="Approved" />
            <el-option label="Implemented" value="Implemented" />
            <el-option label="Archived" value="Archived" />
          </el-select>
          <el-select v-model="filters.complianceStandard" placeholder="Compliance Standard" clearable style="width: 180px">
            <el-option label="IFRS S2" value="IFRS S2" />
            <el-option label="ISSB" value="ISSB" />
            <el-option label="GRI" value="GRI" />
            <el-option label="TCFD" value="TCFD" />
            <el-option label="CSRD" value="CSRD" />
          </el-select>
          <el-date-picker
              v-model="filters.dateRange"
              type="daterange"
              range-separator="to"
              start-placeholder="Start Date"
              end-placeholder="End Date"
              style="width: 280px"
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
          <span>ESG Decisions List</span>
          <div class="table-actions">
            <el-button :icon="Refresh" @click="fetchDecisions" circle />
            <el-button :icon="Setting" @click="handleColumnSettings" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedDecisions" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="title" label="Decision Title" min-width="200" show-overflow-tooltip />
        <el-table-column prop="pillar" label="ESG Pillar" width="120">
          <template #default="{ row }">
            <el-tag :type="getPillarTag(row.pillar)" size="small">{{ row.pillar }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="complianceStandard" label="Compliance Standard" width="120" show-overflow-tooltip />
        <el-table-column prop="carbonImpact" label="Carbon Impact (tCO₂e)" width="150">
          <template #default="{ row }">
            <span :style="{ color: row.carbonImpact < 0 ? '#67c23a' : '#f56c6c' }">
              {{ row.carbonImpact > 0 ? '+' : '' }}{{ row.carbonImpact }} tCO₂e
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="investmentAmount" label="Investment (USD)" width="140">
          <template #default="{ row }">
            ${{ row.investmentAmount.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="expectedROI" label="Expected ROI" width="100">
          <template #default="{ row }">
            <span :style="{ color: row.expectedROI >= 0 ? '#67c23a' : '#f56c6c' }">
              {{ row.expectedROI >= 0 ? '+' : '' }}{{ row.expectedROI }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="decisionMaker" label="Decision Maker" width="130" />
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
    <el-dialog v-model="dialogVisible" :title="dialogMode === 'create' ? 'New ESG Decision' : (dialogMode === 'edit' ? 'Edit ESG Decision' : 'ESG Decision Details')" width="750px" destroy-on-close>
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="140px" :disabled="dialogMode === 'view'">
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="Decision Title" prop="title">
              <el-input v-model="formData.title" placeholder="Enter decision title" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="ESG Pillar" prop="pillar">
              <el-select v-model="formData.pillar" placeholder="Select pillar" style="width: 100%">
                <el-option label="Environmental" value="Environmental" />
                <el-option label="Social" value="Social" />
                <el-option label="Governance" value="Governance" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Status" prop="status">
              <el-select v-model="formData.status" placeholder="Select status" style="width: 100%">
                <el-option label="Draft" value="Draft" />
                <el-option label="In Review" value="In Review" />
                <el-option label="Approved" value="Approved" />
                <el-option label="Implemented" value="Implemented" />
                <el-option label="Archived" value="Archived" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Compliance Standard" prop="complianceStandard">
              <el-select v-model="formData.complianceStandard" placeholder="Select standard" style="width: 100%">
                <el-option label="IFRS S2" value="IFRS S2" />
                <el-option label="ISSB" value="ISSB" />
                <el-option label="GRI" value="GRI" />
                <el-option label="TCFD" value="TCFD" />
                <el-option label="CSRD" value="CSRD" />
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
            <el-form-item label="Investment Amount (USD)" prop="investmentAmount">
              <el-input-number v-model="formData.investmentAmount" :min="0" :step="10000" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Expected ROI (%)" prop="expectedROI">
              <el-input-number v-model="formData.expectedROI" :min="-50" :max="200" :step="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Carbon Impact (tCO₂e)" prop="carbonImpact">
              <el-input-number v-model="formData.carbonImpact" :step="10" style="width: 100%" />
              <span style="margin-left: 8px; color: #909399">negative = reduction</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Social Impact Score" prop="socialImpactScore">
              <el-rate v-model="formData.socialImpactScore" :max="10" show-score style="margin-top: 8px" />
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
      <p>Are you sure you want to delete ESG decision "{{ deleteTarget?.title }}"?</p>
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
  'Loading ESG decisions...',
  'Fetching compliance data...',
  'Almost ready...'
]

// ==================== Interfaces ====================
interface ESGDecision {
  id: number
  title: string
  pillar: string
  status: string
  complianceStandard: string
  carbonImpact: number
  investmentAmount: number
  expectedROI: number
  decisionMaker: string
  decisionDate: string
  socialImpactScore: number
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
const esgChartRef = ref<HTMLElement>()
const pillarChartRef = ref<HTMLElement>()
let esgChart: echarts.ECharts | null = null
let pillarChart: echarts.ECharts | null = null

const esgTimeRange = ref<'quarter' | 'year'>('quarter')

// ==================== Mock Data ====================
const statsCards = ref<StatCard[]>([
  { title: 'Total ESG Decisions', value: 86, trend: 18, icon: 'Document', bgColor: '#409eff', key: 'total' },
  { title: 'Total Investment', value: '$12.4M', trend: 24, icon: 'TrendCharts', bgColor: '#67c23a', key: 'investment' },
  { title: 'Carbon Reduction', value: '8,450 tCO₂e', trend: -32, icon: 'Checked', bgColor: '#409eff', key: 'carbon' },
  { title: 'Compliance Rate', value: '94%', trend: 5, icon: 'Clock', bgColor: '#e6a23c', key: 'compliance' }
])

const esgDecisions = ref<ESGDecision[]>([
  {
    id: 1,
    title: 'Solar Panel Installation at Data Center',
    pillar: 'Environmental',
    status: 'Implemented',
    complianceStandard: 'IFRS S2',
    carbonImpact: -1250,
    investmentAmount: 2500000,
    expectedROI: 15,
    decisionMaker: 'Sarah Chen',
    decisionDate: '2024-01-05',
    socialImpactScore: 8,
    description: 'Install 5MW solar panels across data center roof',
    expectedOutcomes: '30% reduction in grid electricity consumption'
  },
  {
    id: 2,
    title: 'Employee Diversity & Inclusion Program',
    pillar: 'Social',
    status: 'In Review',
    complianceStandard: 'GRI',
    carbonImpact: 0,
    investmentAmount: 500000,
    expectedROI: -5,
    decisionMaker: 'Michael Lee',
    decisionDate: '2024-01-10',
    socialImpactScore: 9,
    description: 'Comprehensive D&I initiative targeting leadership diversity',
    expectedOutcomes: '40% diverse representation in management by 2026'
  },
  {
    id: 3,
    title: 'Board Independence Restructuring',
    pillar: 'Governance',
    status: 'Approved',
    complianceStandard: 'ISSB',
    carbonImpact: 0,
    investmentAmount: 150000,
    expectedROI: 8,
    decisionMaker: 'James Wilson',
    decisionDate: '2023-12-20',
    socialImpactScore: 7,
    description: 'Increase independent board members to 60%',
    expectedOutcomes: 'Improved governance score and investor confidence'
  },
  {
    id: 4,
    title: 'Electric Vehicle Fleet Transition',
    pillar: 'Environmental',
    status: 'In Progress',
    complianceStandard: 'TCFD',
    carbonImpact: -580,
    investmentAmount: 1800000,
    expectedROI: 12,
    decisionMaker: 'Emily Zhao',
    decisionDate: '2024-01-08',
    socialImpactScore: 8,
    description: 'Replace 50 fleet vehicles with EVs',
    expectedOutcomes: 'Scope 1 reduction of 580 tCO₂e annually'
  },
  {
    id: 5,
    title: 'Water Conservation System Upgrade',
    pillar: 'Environmental',
    status: 'Implemented',
    complianceStandard: 'CSRD',
    carbonImpact: -120,
    investmentAmount: 750000,
    expectedROI: 10,
    decisionMaker: 'David Wang',
    decisionDate: '2023-12-15',
    socialImpactScore: 7,
    description: 'Install water recycling and rainwater harvesting',
    expectedOutcomes: '40% reduction in water consumption'
  },
  {
    id: 6,
    title: 'Supplier Code of Conduct Enforcement',
    pillar: 'Governance',
    status: 'In Review',
    complianceStandard: 'GRI',
    carbonImpact: -200,
    investmentAmount: 300000,
    expectedROI: 6,
    decisionMaker: 'Lisa Zhang',
    decisionDate: '2024-01-12',
    socialImpactScore: 8,
    description: 'Mandatory ESG compliance for top 100 suppliers',
    expectedOutcomes: 'Supply chain emissions reduction of 200 tCO₂e'
  },
  {
    id: 7,
    title: 'Green Building Certification Program',
    pillar: 'Environmental',
    status: 'Approved',
    complianceStandard: 'IFRS S2',
    carbonImpact: -850,
    investmentAmount: 3200000,
    expectedROI: 9,
    decisionMaker: 'Tom Harris',
    decisionDate: '2024-01-03',
    socialImpactScore: 8,
    description: 'LEED Platinum certification for headquarters',
    expectedOutcomes: 'Energy efficiency improvement of 25%'
  },
  {
    id: 8,
    title: 'Community Education Scholarship Fund',
    pillar: 'Social',
    status: 'Implemented',
    complianceStandard: 'GRI',
    carbonImpact: 0,
    investmentAmount: 1000000,
    expectedROI: -2,
    decisionMaker: 'Anna Kim',
    decisionDate: '2023-12-28',
    socialImpactScore: 10,
    description: 'Annual scholarships for underserved communities',
    expectedOutcomes: '100 students supported annually'
  },
  {
    id: 9,
    title: 'Carbon Offset Investment Strategy',
    pillar: 'Environmental',
    status: 'Draft',
    complianceStandard: 'ISSB',
    carbonImpact: -3000,
    investmentAmount: 4500000,
    expectedROI: 4,
    decisionMaker: 'John Smith',
    decisionDate: '2024-01-14',
    socialImpactScore: 6,
    description: 'Investment in verified carbon offset projects',
    expectedOutcomes: 'Carbon neutrality achievement by 2025'
  },
  {
    id: 10,
    title: 'Whistleblower Protection Policy',
    pillar: 'Governance',
    status: 'Approved',
    complianceStandard: 'CSRD',
    carbonImpact: 0,
    investmentAmount: 100000,
    expectedROI: 3,
    decisionMaker: 'Robert Liu',
    decisionDate: '2024-01-07',
    socialImpactScore: 9,
    description: 'Enhanced anonymous reporting mechanism',
    expectedOutcomes: 'Improved ethical compliance and reporting'
  },
  {
    id: 11,
    title: 'Green Bond Issuance',
    pillar: 'Environmental',
    status: 'In Review',
    complianceStandard: 'TCFD',
    carbonImpact: -5000,
    investmentAmount: 50000000,
    expectedROI: 7,
    decisionMaker: 'Sarah Chen',
    decisionDate: '2024-01-11',
    socialImpactScore: 7,
    description: '$50M green bond for sustainable projects',
    expectedOutcomes: 'Funding for 5 major environmental initiatives'
  },
  {
    id: 12,
    title: 'Wellness Program Expansion',
    pillar: 'Social',
    status: 'Implemented',
    complianceStandard: 'GRI',
    carbonImpact: 0,
    investmentAmount: 400000,
    expectedROI: 15,
    decisionMaker: 'Emily Zhao',
    decisionDate: '2023-12-18',
    socialImpactScore: 9,
    description: 'Mental health and wellness benefits for all employees',
    expectedOutcomes: 'Increased employee satisfaction and retention'
  }
])

// ==================== Reactive Variables ====================
const tableLoading = ref(false)
const dialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit' | 'view'>('view')
const deleteTarget = ref<ESGDecision | null>(null)
const formRef = ref()
const currentPage = ref(1)
const pageSize = ref(10)

const filters = reactive({
  keyword: '',
  pillar: '',
  status: '',
  complianceStandard: '',
  dateRange: null as [Date, Date] | null
})

const formData = reactive<ESGDecision>({
  id: 0,
  title: '',
  pillar: 'Environmental',
  status: 'Draft',
  complianceStandard: 'IFRS S2',
  carbonImpact: 0,
  investmentAmount: 0,
  expectedROI: 0,
  decisionMaker: '',
  decisionDate: new Date().toISOString().split('T')[0],
  socialImpactScore: 5,
  description: '',
  expectedOutcomes: ''
})

const formRules = {
  title: [{ required: true, message: 'Please enter decision title', trigger: 'blur' }],
  pillar: [{ required: true, message: 'Please select ESG pillar', trigger: 'change' }],
  status: [{ required: true, message: 'Please select status', trigger: 'change' }],
  complianceStandard: [{ required: true, message: 'Please select compliance standard', trigger: 'change' }],
  decisionMaker: [{ required: true, message: 'Please enter decision maker', trigger: 'blur' }]
}

// ==================== Computed ====================
const filteredDecisions = computed(() => {
  let filtered = [...esgDecisions.value]

  if (filters.keyword) {
    filtered = filtered.filter(d =>
        d.title.toLowerCase().includes(filters.keyword.toLowerCase()) ||
        d.description.toLowerCase().includes(filters.keyword.toLowerCase())
    )
  }

  if (filters.pillar) {
    filtered = filtered.filter(d => d.pillar === filters.pillar)
  }

  if (filters.status) {
    filtered = filtered.filter(d => d.status === filters.status)
  }

  if (filters.complianceStandard) {
    filtered = filtered.filter(d => d.complianceStandard === filters.complianceStandard)
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
const getPillarTag = (pillar: string): string => {
  const map: Record<string, string> = {
    'Environmental': 'success',
    'Social': 'warning',
    'Governance': 'info'
  }
  return map[pillar] || 'info'
}

const getStatusTag = (status: string): string => {
  const map: Record<string, string> = {
    'Draft': 'info',
    'In Review': 'warning',
    'Approved': 'primary',
    'Implemented': 'success',
    'Archived': 'danger'
  }
  return map[status] || 'info'
}

// ==================== Chart Initialization ====================
const initESGChart = () => {
  if (!esgChartRef.value) return
  if (esgChart) esgChart.dispose()

  esgChart = echarts.init(esgChartRef.value)
  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['Environmental', 'Social', 'Governance', 'Overall ESG'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '12%', containLabel: true },
    xAxis: { type: 'category', data: ['Q1', 'Q2', 'Q3', 'Q4'] },
    yAxis: { type: 'value', name: 'Score', min: 0, max: 100 },
    series: [
      { name: 'Environmental', type: 'line', data: [65, 68, 72, 78], smooth: true, lineStyle: { width: 3 }, symbolSize: 8 },
      { name: 'Social', type: 'line', data: [70, 73, 75, 80], smooth: true, lineStyle: { width: 3 }, symbolSize: 8 },
      { name: 'Governance', type: 'line', data: [75, 76, 78, 82], smooth: true, lineStyle: { width: 3 }, symbolSize: 8 },
      { name: 'Overall ESG', type: 'line', data: [70, 72, 75, 80], smooth: true, lineStyle: { width: 4, color: '#409eff' }, symbolSize: 10 }
    ]
  }
  esgChart.setOption(option)
  window.addEventListener('resize', () => esgChart?.resize())
}

const initPillarChart = () => {
  if (!pillarChartRef.value) return
  if (pillarChart) pillarChart.dispose()

  pillarChart = echarts.init(pillarChartRef.value)
  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [
      {
        name: 'ESG Pillars',
        type: 'pie',
        radius: '55%',
        data: [
          { value: 45, name: 'Environmental', itemStyle: { color: '#67c23a' } },
          { value: 28, name: 'Social', itemStyle: { color: '#e6a23c' } },
          { value: 27, name: 'Governance', itemStyle: { color: '#409eff' } }
        ],
        emphasis: { scale: true },
        label: { show: true, formatter: '{b}: {d}%' }
      }
    ]
  }
  pillarChart.setOption(option)
  window.addEventListener('resize', () => pillarChart?.resize())
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
  filters.pillar = ''
  filters.status = ''
  filters.complianceStandard = ''
  filters.dateRange = null
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

const handleExport = () => {
  ElMessage.success(`Exporting ${filteredDecisions.value.length} ESG decisions...`)
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
    pillar: 'Environmental',
    status: 'Draft',
    complianceStandard: 'IFRS S2',
    carbonImpact: 0,
    investmentAmount: 0,
    expectedROI: 0,
    decisionMaker: '',
    decisionDate: new Date().toISOString().split('T')[0],
    socialImpactScore: 5,
    description: '',
    expectedOutcomes: ''
  })
  dialogVisible.value = true
}

const viewDetail = (row: ESGDecision) => {
  dialogMode.value = 'view'
  Object.assign(formData, row)
  dialogVisible.value = true
}

const editDecision = (row: ESGDecision) => {
  dialogMode.value = 'edit'
  Object.assign(formData, row)
  dialogVisible.value = true
}

const deleteDecision = (row: ESGDecision) => {
  deleteTarget.value = row
  deleteDialogVisible.value = true
}

const confirmDelete = () => {
  if (deleteTarget.value) {
    const index = esgDecisions.value.findIndex(d => d.id === deleteTarget.value!.id)
    if (index !== -1) {
      esgDecisions.value.splice(index, 1)
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
        esgDecisions.value.unshift({ ...formData, id: Date.now() })
        ElMessage.success('ESG decision created successfully')
      } else if (dialogMode.value === 'edit') {
        const index = esgDecisions.value.findIndex(d => d.id === formData.id)
        if (index !== -1) {
          esgDecisions.value[index] = { ...formData }
          ElMessage.success('ESG decision updated successfully')
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
    initESGChart()
    initPillarChart()
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
.esg-decisions-page {
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

.esg-score-card, .stats-card {
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
  height: 280px;
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

:deep(.el-rate) {
  display: inline-flex;
}
</style>