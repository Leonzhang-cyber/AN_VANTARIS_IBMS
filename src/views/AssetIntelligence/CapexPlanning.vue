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
          <span class="loading-title">CAPEX Planning</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Capital Expenditure Planning & Budget Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="capex-planning-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Money /></el-icon>
          CAPEX Planning
        </h1>
        <div class="page-subtitle">Capital expenditure planning, budget allocation, and investment optimization</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openBudgetDialog">
          <el-icon><Plus /></el-icon> Create Budget
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
          <el-icon><Money /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">${{ stats.totalCAPEX.toLocaleString() }}</div>
          <div class="stat-label">Total CAPEX (5 Years)</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.approvedProjects }}</div>
          <div class="stat-label">Approved Projects</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.pendingProjects }}</div>
          <div class="stat-label">Pending Projects</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">${{ stats.budgetGap.toLocaleString() }}</div>
          <div class="stat-label">Budget Gap</div>
          <div class="stat-trend down">Funding shortfall</div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Row -->
    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-title">Annual CAPEX Budget</div>
        <div class="metric-value">${{ metrics.annualBudget.toLocaleString() }}</div>
        <div class="metric-trend" :class="metrics.budgetTrend > 0 ? 'positive' : 'negative'">
          {{ metrics.budgetTrend > 0 ? '↑' : '↓' }} {{ Math.abs(metrics.budgetTrend) }}% vs last year
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Budget Utilization</div>
        <div class="metric-value">{{ metrics.utilization }}<span class="metric-unit">%</span></div>
        <el-progress :percentage="metrics.utilization" :stroke-width="8" :color="metrics.utilization > 90 ? '#ef4444' : (metrics.utilization > 70 ? '#f59e0b' : '#22c55e')" />
      </div>
      <div class="metric-card">
        <div class="metric-title">Projected ROI</div>
        <div class="metric-value">{{ metrics.projectedROI }}<span class="metric-unit">%</span></div>
        <div class="metric-trend positive">↑ {{ metrics.roiGrowth }}% vs last year</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Average Payback Period</div>
        <div class="metric-value">{{ metrics.avgPayback }}<span class="metric-unit">years</span></div>
        <div class="metric-trend positive">Optimizing</div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">CAPEX Forecast (5 Years)</span>
          <span class="chart-subtitle">Budget vs Actual projection</span>
        </div>
        <div class="chart-container" ref="forecastChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Budget Allocation by Category</span>
          <span class="chart-subtitle">CAPEX distribution</span>
        </div>
        <div class="chart-container" ref="allocationChartEl"></div>
      </div>
    </div>

    <!-- Second Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Quarterly Spending Trend</span>
          <span class="chart-subtitle">Actual vs Planned</span>
        </div>
        <div class="chart-container" ref="quarterlyChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">ROI by Project Category</span>
          <span class="chart-subtitle">Expected returns</span>
        </div>
        <div class="chart-container" ref="roiChartEl"></div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-input
            v-model="searchText"
            placeholder="Search by project name or category..."
            style="width: 240px"
            clearable
            :prefix-icon="Search"
        />
        <el-select v-model="categoryFilter" placeholder="Category" clearable style="width: 140px">
          <el-option v-for="c in uniqueCategories" :key="c" :label="c" :value="c" />
        </el-select>
        <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 130px">
          <el-option label="Approved" value="approved" />
          <el-option label="Pending" value="pending" />
          <el-option label="In Progress" value="in-progress" />
          <el-option label="Completed" value="completed" />
          <el-option label="Rejected" value="rejected" />
        </el-select>
        <el-select v-model="priorityFilter" placeholder="Priority" clearable style="width: 120px">
          <el-option label="Critical" value="Critical" />
          <el-option label="High" value="High" />
          <el-option label="Medium" value="Medium" />
          <el-option label="Low" value="Low" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button type="primary" link @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon> Reset Filters
        </el-button>
      </div>
    </div>

    <!-- CAPEX Projects Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">CAPEX Projects</span>
        <el-button size="small" @click="viewAllProjects">View All →</el-button>
      </div>
      <el-table :data="paginatedProjects" stripe style="width: 100%" v-loading="tableLoading"
                @row-click="viewProjectDetail">
        <el-table-column prop="id" label="Project ID" width="120" />
        <el-table-column prop="name" label="Project Name" min-width="200" />
        <el-table-column prop="category" label="Category" width="130">
          <template #default="{ row }">
            <el-tag :type="getCategoryTagType(row.category)" size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="Priority" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityTagType(row.priority)" size="small">{{ row.priority }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="budget" label="Budget" width="140">
          <template #default="{ row }">
            ${{ row.budget.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="actualSpent" label="Actual Spent" width="140">
          <template #default="{ row }">
            ${{ row.actualSpent.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="roi" label="Expected ROI" width="100">
          <template #default="{ row }">
            <span :class="row.roi > 15 ? 'metric-good' : (row.roi > 8 ? 'metric-warning' : 'metric-bad')">
              {{ row.roi }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="paybackYears" label="Payback" width="100">
          <template #default="{ row }">
            {{ row.paybackYears }} yrs
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click.stop="viewProjectDetail(row)">Details</el-button>
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

    <!-- Project Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="selectedProject?.name" width="900px" class="project-dialog">
      <div v-if="selectedProject" class="project-detail">
        <!-- Header Stats -->
        <div class="detail-header-stats">
          <div class="detail-stat">
            <div class="detail-stat-value">${{ selectedProject.budget.toLocaleString() }}</div>
            <div class="detail-stat-label">Total Budget</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">${{ selectedProject.actualSpent.toLocaleString() }}</div>
            <div class="detail-stat-label">Actual Spent</div>
            <div class="detail-stat-sub">{{ ((selectedProject.actualSpent / selectedProject.budget) * 100).toFixed(1) }}% utilized</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedProject.roi }}%</div>
            <div class="detail-stat-label">Expected ROI</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedProject.paybackYears }} yrs</div>
            <div class="detail-stat-label">Payback Period</div>
          </div>
        </div>

        <!-- Basic Info -->
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Project ID">{{ selectedProject.id }}</el-descriptions-item>
          <el-descriptions-item label="Category">
            <el-tag :type="getCategoryTagType(selectedProject.category)" size="small">{{ selectedProject.category }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusTagType(selectedProject.status)" size="small">{{ getStatusText(selectedProject.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Priority">
            <el-tag :type="getPriorityTagType(selectedProject.priority)" size="small">{{ selectedProject.priority }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Start Date">{{ selectedProject.startDate }}</el-descriptions-item>
          <el-descriptions-item label="End Date">{{ selectedProject.endDate }}</el-descriptions-item>
          <el-descriptions-item label="Department">{{ selectedProject.department }}</el-descriptions-item>
          <el-descriptions-item label="Project Manager">{{ selectedProject.projectManager }}</el-descriptions-item>
        </el-descriptions>

        <!-- Spending Breakdown -->
        <div class="detail-section">
          <div class="section-title">Spending Breakdown</div>
          <el-table :data="selectedProject.spendingBreakdown" border stripe>
            <el-table-column prop="item" label="Item" width="200" />
            <el-table-column prop="amount" label="Amount" width="150">
              <template #default="{ row }">
                ${{ row.amount.toLocaleString() }}
              </template>
            </el-table-column>
            <el-table-column prop="percentage" label="Percentage" width="150">
              <template #default="{ row }">
                <el-progress :percentage="row.percentage" :stroke-width="6" :color="'#3b82f6'" />
              </template>
            </el-table-column>
            <el-table-column prop="status" label="Status" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'Completed' ? 'success' : (row.status === 'In Progress' ? 'warning' : 'info')" size="small">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="notes" label="Notes" min-width="200" />
          </el-table>
        </div>

        <!-- Milestones -->
        <div class="detail-section">
          <div class="section-title">Project Milestones</div>
          <el-timeline>
            <el-timeline-item
                v-for="milestone in selectedProject.milestones"
                :key="milestone.id"
                :timestamp="milestone.date"
                :type="milestone.status === 'Completed' ? 'success' : (milestone.status === 'In Progress' ? 'primary' : 'info')"
                placement="top"
            >
              <div class="milestone-content">
                <span class="milestone-title">{{ milestone.title }}</span>
                <span class="milestone-status">
                  <el-tag :type="milestone.status === 'Completed' ? 'success' : (milestone.status === 'In Progress' ? 'warning' : 'info')" size="small">
                    {{ milestone.status }}
                  </el-tag>
                </span>
                <div class="milestone-description">{{ milestone.description }}</div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>

        <!-- Justification -->
        <div class="detail-section">
          <div class="section-title">Business Justification</div>
          <el-alert
              :title="selectedProject.justification.title"
              :type="selectedProject.justification.type"
              :description="selectedProject.justification.description"
              :closable="false"
              show-icon
          />
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" v-if="selectedProject?.status === 'pending'" @click="approveProject(selectedProject)">Approve</el-button>
        <el-button type="warning" v-if="selectedProject?.status === 'pending'" @click="rejectProject(selectedProject)">Reject</el-button>
        <el-button type="success" v-if="selectedProject?.status === 'approved'" @click="updateStatus(selectedProject)">Update Status</el-button>
      </template>
    </el-dialog>

    <!-- Create Budget Dialog -->
    <el-dialog v-model="budgetDialogVisible" title="Create Budget" width="550px">
      <el-form :model="budgetForm" label-width="140px">
        <el-form-item label="Fiscal Year" required>
          <el-select v-model="budgetForm.year" style="width: 100%">
            <el-option :label="new Date().getFullYear().toString()" :value="new Date().getFullYear().toString()" />
            <el-option :label="(new Date().getFullYear() + 1).toString()" :value="(new Date().getFullYear() + 1).toString()" />
            <el-option :label="(new Date().getFullYear() + 2).toString()" :value="(new Date().getFullYear() + 2).toString()" />
          </el-select>
        </el-form-item>
        <el-form-item label="Total Budget" required>
          <el-input-number v-model="budgetForm.totalBudget" :min="0" :step="100000" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Budget by Category" required>
          <div class="category-budget-list">
            <div v-for="cat in budgetCategories" :key="cat" class="category-budget-item">
              <span class="category-name">{{ cat }}</span>
              <el-input-number v-model="budgetForm.categoryBudget[cat]" :min="0" :step="10000" size="small" style="width: 150px" />
            </div>
          </div>
        </el-form-item>
        <el-form-item label="Notes">
          <el-input v-model="budgetForm.notes" type="textarea" :rows="2" placeholder="Additional notes..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="budgetDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveBudget">Create Budget</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Money, Plus, Download, Refresh, TrendCharts, Clock, Warning,
  Search, RefreshLeft
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading CAPEX data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading CAPEX data...',
  'Analyzing budget allocation...',
  'Calculating ROI projections...',
  'Loading project details...',
  'Almost ready...'
]

// ==================== Types ====================
interface SpendingItem {
  item: string
  amount: number
  percentage: number
  status: string
  notes: string
}

interface Milestone {
  id: number
  date: string
  title: string
  description: string
  status: string
}

interface Justification {
  title: string
  type: 'success' | 'warning' | 'info' | 'error'
  description: string
}

interface CAPEXProject {
  id: string
  name: string
  category: string
  status: string
  priority: string
  budget: number
  actualSpent: number
  roi: number
  paybackYears: number
  startDate: string
  endDate: string
  department: string
  projectManager: string
  spendingBreakdown: SpendingItem[]
  milestones: Milestone[]
  justification: Justification
}

// ==================== Mock Data (60 CAPEX projects) ====================
const generateCAPEXData = (): CAPEXProject[] => {
  const categories = ['UPS Replacement', 'Generator Upgrade', 'CRAC Installation', 'Chiller Replacement',
    'Switchgear Upgrade', 'Server Refresh', 'Storage Expansion', 'Network Upgrade',
    'Cooling System', 'Power Distribution', 'Battery Replacement', 'Facility Renovation']
  const departments = ['IT Infrastructure', 'Facilities', 'Data Center Operations', 'Engineering', 'Security']
  const managers = ['John Tan', 'Mike Chen', 'Ahmad Ibrahim', 'Lim Wei Ming', 'Sarah Koh', 'David Lee', 'Priya Sharma']
  const statuses = ['approved', 'pending', 'in-progress', 'completed', 'rejected']
  const priorities = ['Critical', 'High', 'Medium', 'Low']

  const projects: CAPEXProject[] = []

  for (let i = 1; i <= 60; i++) {
    const category = categories[Math.floor(Math.random() * categories.length)]
    const status = statuses[Math.floor(Math.random() * statuses.length)]
    const priority = priorities[Math.floor(Math.random() * priorities.length)]

    const budget = [50000, 100000, 150000, 250000, 500000, 1000000][Math.floor(Math.random() * 6)] * (0.5 + Math.random())
    const budgetAmount = Math.round(budget / 1000) * 1000

    let actualSpent = 0
    if (status === 'completed') {
      actualSpent = Math.round(budgetAmount * (0.9 + Math.random() * 0.2))
    } else if (status === 'in-progress') {
      actualSpent = Math.round(budgetAmount * (0.3 + Math.random() * 0.5))
    } else {
      actualSpent = Math.round(budgetAmount * (0.05 + Math.random() * 0.1))
    }

    const roi = parseFloat((8 + Math.random() * 20).toFixed(1))
    const paybackYears = parseFloat((2 + Math.random() * 5).toFixed(1))

    const startDate = new Date()
    startDate.setMonth(startDate.getMonth() - Math.random() * 12)
    const startDateStr = startDate.toISOString().slice(0, 10)

    const endDate = new Date(startDate)
    endDate.setMonth(endDate.getMonth() + 6 + Math.random() * 12)
    const endDateStr = endDate.toISOString().slice(0, 10)

    // Generate spending breakdown
    const spendingItems = [
      { item: 'Equipment Purchase', amount: Math.round(budgetAmount * 0.6), percentage: 60, status: status === 'completed' ? 'Completed' : (status === 'in-progress' ? 'In Progress' : 'Planned'), notes: 'Main hardware and components' },
      { item: 'Installation & Labor', amount: Math.round(budgetAmount * 0.2), percentage: 20, status: status === 'completed' ? 'Completed' : (status === 'in-progress' ? 'In Progress' : 'Planned'), notes: 'Professional installation services' },
      { item: 'Software & Licensing', amount: Math.round(budgetAmount * 0.1), percentage: 10, status: status === 'completed' ? 'Completed' : (status === 'in-progress' ? 'Partially Completed' : 'Planned'), notes: 'Software licenses and subscriptions' },
      { item: 'Training & Documentation', amount: Math.round(budgetAmount * 0.05), percentage: 5, status: 'Planned', notes: 'Staff training and technical documentation' },
      { item: 'Contingency', amount: Math.round(budgetAmount * 0.05), percentage: 5, status: 'Planned', notes: 'Unforeseen expenses buffer' }
    ]

    // Generate milestones
    const milestones: Milestone[] = [
      { id: 1, date: startDateStr, title: 'Project Initiation', description: 'Project charter approved and team assembled', status: new Date(startDateStr) < new Date() ? 'Completed' : 'Pending' },
      { id: 2, date: new Date(startDate.getTime() + 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10), title: 'Requirements & Design', description: 'Technical requirements and solution design completed', status: new Date(startDate.getTime() + 30 * 24 * 60 * 60 * 1000) < new Date() ? (status === 'completed' ? 'Completed' : 'In Progress') : 'Pending' },
      { id: 3, date: new Date(startDate.getTime() + 90 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10), title: 'Procurement', description: 'Equipment and services procured', status: 'Pending' },
      { id: 4, date: new Date(startDate.getTime() + 150 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10), title: 'Installation', description: 'Equipment installation and configuration', status: 'Pending' },
      { id: 5, date: endDateStr, title: 'Project Completion', description: 'Final acceptance and project closure', status: status === 'completed' ? 'Completed' : 'Pending' }
    ]

    // Generate justification
    let justification: Justification
    if (roi > 20) {
      justification = { title: 'High ROI Investment', type: 'success', description: `Project expected to deliver ${roi}% ROI with payback period of ${paybackYears} years. Strong financial justification.` }
    } else if (roi > 12) {
      justification = { title: 'Moderate ROI Investment', type: 'info', description: `Project expected to deliver ${roi}% ROI. Aligns with strategic objectives.` }
    } else {
      justification = { title: 'Essential Infrastructure', type: 'warning', description: `Critical infrastructure upgrade with ${roi}% ROI. Required for business continuity and compliance.` }
    }

    projects.push({
      id: `CAPEX-${String(i).padStart(4, '0')}`,
      name: `${category} ${String.fromCharCode(64 + Math.ceil(i / 10))}${((i - 1) % 10) + 1}`,
      category: category,
      status: status,
      priority: priority,
      budget: budgetAmount,
      actualSpent: actualSpent,
      roi: roi,
      paybackYears: paybackYears,
      startDate: startDateStr,
      endDate: endDateStr,
      department: departments[Math.floor(Math.random() * departments.length)],
      projectManager: managers[Math.floor(Math.random() * managers.length)],
      spendingBreakdown: spendingItems,
      milestones: milestones,
      justification: justification
    })
  }

  return projects
}

const projects = ref<CAPEXProject[]>(generateCAPEXData())

// ==================== State ====================
const searchText = ref('')
const categoryFilter = ref('')
const statusFilter = ref('')
const priorityFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)
const budgetDialogVisible = ref(false)
const selectedProject = ref<CAPEXProject | null>(null)

// Chart refs
let forecastChart: echarts.ECharts | null = null
let allocationChart: echarts.ECharts | null = null
let quarterlyChart: echarts.ECharts | null = null
let roiChart: echarts.ECharts | null = null

const forecastChartEl = ref<HTMLElement | null>(null)
const allocationChartEl = ref<HTMLElement | null>(null)
const quarterlyChartEl = ref<HTMLElement | null>(null)
const roiChartEl = ref<HTMLElement | null>(null)

const budgetForm = ref({
  year: new Date().getFullYear().toString(),
  totalBudget: 5000000,
  categoryBudget: {} as Record<string, number>,
  notes: ''
})

const budgetCategories = ['UPS Replacement', 'Generator Upgrade', 'CRAC Installation', 'Chiller Replacement',
  'Switchgear Upgrade', 'Server Refresh', 'Storage Expansion', 'Network Upgrade']

// Initialize category budget
budgetCategories.forEach(cat => {
  budgetForm.value.categoryBudget[cat] = 500000
})

// ==================== Computed ====================
const stats = computed(() => {
  const totalCAPEX = projects.value.reduce((sum, p) => sum + p.budget, 0)
  const approvedProjects = projects.value.filter(p => p.status === 'approved' || p.status === 'in-progress' || p.status === 'completed').length
  const pendingProjects = projects.value.filter(p => p.status === 'pending').length
  const currentYearBudget = projects.value.filter(p => p.startDate.startsWith(new Date().getFullYear().toString()))
      .reduce((sum, p) => sum + p.budget, 0)
  const approvedBudget = projects.value.filter(p => p.status === 'approved' || p.status === 'in-progress')
      .reduce((sum, p) => sum + p.budget, 0)
  const budgetGap = currentYearBudget - approvedBudget

  return {
    totalCAPEX: Math.round(totalCAPEX / 1000) * 1000,
    approvedProjects,
    pendingProjects,
    budgetGap: Math.max(0, Math.round(budgetGap / 1000) * 1000)
  }
})

const metrics = computed(() => {
  const currentYearProjects = projects.value.filter(p => p.startDate.startsWith(new Date().getFullYear().toString()))
  const annualBudget = currentYearProjects.reduce((sum, p) => sum + p.budget, 0)
  const annualSpent = currentYearProjects.reduce((sum, p) => sum + p.actualSpent, 0)
  const utilization = annualBudget > 0 ? Math.round((annualSpent / annualBudget) * 100) : 0
  const projectedROI = (projects.value.reduce((sum, p) => sum + p.roi, 0) / projects.value.length).toFixed(1)
  const avgPayback = (projects.value.reduce((sum, p) => sum + p.paybackYears, 0) / projects.value.length).toFixed(1)

  return {
    annualBudget: Math.round(annualBudget / 1000) * 1000,
    budgetTrend: 12.5,
    utilization,
    projectedROI: parseFloat(projectedROI),
    roiGrowth: 3.2,
    avgPayback: parseFloat(avgPayback)
  }
})

const uniqueCategories = computed(() => {
  return [...new Set(projects.value.map(p => p.category))]
})

const filteredProjects = computed(() => {
  let filtered = [...projects.value]

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(p =>
        p.name.toLowerCase().includes(search) ||
        p.id.toLowerCase().includes(search) ||
        p.projectManager.toLowerCase().includes(search)
    )
  }

  if (categoryFilter.value) {
    filtered = filtered.filter(p => p.category === categoryFilter.value)
  }

  if (statusFilter.value) {
    filtered = filtered.filter(p => p.status === statusFilter.value)
  }

  if (priorityFilter.value) {
    filtered = filtered.filter(p => p.priority === priorityFilter.value)
  }

  return filtered
})

const totalRecords = computed(() => filteredProjects.value.length)

const paginatedProjects = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredProjects.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getCategoryTagType = (category: string): string => {
  const categoryMap: Record<string, string> = {
    'UPS Replacement': 'primary',
    'Generator Upgrade': 'warning',
    'CRAC Installation': 'info',
    'Chiller Replacement': 'danger',
    'Switchgear Upgrade': 'success',
    'Server Refresh': '',
    'Storage Expansion': '',
    'Network Upgrade': '',
    'Cooling System': 'info',
    'Power Distribution': 'primary',
    'Battery Replacement': 'warning',
    'Facility Renovation': ''
  }
  return categoryMap[category] || 'info'
}

const getStatusText = (status: string): string => {
  const map: Record<string, string> = {
    approved: 'Approved',
    pending: 'Pending',
    'in-progress': 'In Progress',
    completed: 'Completed',
    rejected: 'Rejected'
  }
  return map[status] || status
}

const getStatusTagType = (status: string): string => {
  const map: Record<string, string> = {
    approved: 'success',
    pending: 'warning',
    'in-progress': 'primary',
    completed: 'info',
    rejected: 'danger'
  }
  return map[status] || 'info'
}

const getPriorityTagType = (priority: string): string => {
  const map: Record<string, string> = { Critical: 'danger', High: 'warning', Medium: 'info', Low: 'success' }
  return map[priority] || 'info'
}

const resetFilters = () => {
  searchText.value = ''
  categoryFilter.value = ''
  statusFilter.value = ''
  priorityFilter.value = ''
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
  const budgetData = [2500, 2800, 3100, 2900, 2700]
  const actualData = [2300, 2600, null, null, null]

  forecastChart = echarts.init(forecastChartEl.value)
  forecastChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Budget Forecast', 'Actual Spending'], bottom: 0 },
    grid: { top: 40, left: 60, right: 30, bottom: 40 },
    xAxis: { type: 'category', data: years },
    yAxis: { type: 'value', name: 'CAPEX ($K)' },
    series: [
      { name: 'Budget Forecast', type: 'line', data: budgetData, lineStyle: { color: '#3b82f6', width: 3 }, symbol: 'circle', symbolSize: 8, label: { show: true, position: 'top', formatter: '${c}K' } },
      { name: 'Actual Spending', type: 'bar', data: actualData, itemStyle: { color: '#22c55e', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top', formatter: '${c}K' } }
    ]
  })
}

const initAllocationChart = () => {
  if (!allocationChartEl.value) return
  if (allocationChart) {
    allocationChart.dispose()
    allocationChart = null
  }

  const categoryMap = new Map<string, number>()
  projects.value.forEach(p => {
    categoryMap.set(p.category, (categoryMap.get(p.category) || 0) + p.budget)
  })

  const data = Array.from(categoryMap.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8)
      .map(([name, value]) => ({ name, value: Math.round(value / 1000) }))

  allocationChart = echarts.init(allocationChartEl.value)
  allocationChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}<br/>Budget: ${c}K' },
    legend: { orient: 'vertical', left: 'left', data: data.map(d => d.name), type: 'scroll' },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: data,
      label: { show: true, formatter: '{b}: ${c}K', fontSize: 10 },
      emphasis: { scale: true }
    }]
  })
}

const initQuarterlyChart = () => {
  if (!quarterlyChartEl.value) return
  if (quarterlyChart) {
    quarterlyChart.dispose()
    quarterlyChart = null
  }

  const quarters = ['Q1', 'Q2', 'Q3', 'Q4']
  const planned = [1200, 1500, 1800, 1400]
  const actual = [1100, 1450, 1650, null]

  quarterlyChart = echarts.init(quarterlyChartEl.value)
  quarterlyChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Planned', 'Actual'], bottom: 0 },
    grid: { top: 40, left: 60, right: 30, bottom: 40 },
    xAxis: { type: 'category', data: quarters },
    yAxis: { type: 'value', name: 'CAPEX ($K)' },
    series: [
      { name: 'Planned', type: 'bar', data: planned, itemStyle: { color: '#3b82f6', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top', formatter: '${c}K' } },
      { name: 'Actual', type: 'bar', data: actual, itemStyle: { color: '#22c55e', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top', formatter: '${c}K' } }
    ]
  })
}

const initRoiChart = () => {
  if (!roiChartEl.value) return
  if (roiChart) {
    roiChart.dispose()
    roiChart = null
  }

  const categories = ['UPS Replacement', 'Generator Upgrade', 'CRAC Installation', 'Chiller Replacement', 'Server Refresh', 'Network Upgrade']
  const rois = categories.map(cat => {
    const catProjects = projects.value.filter(p => p.category === cat)
    if (catProjects.length === 0) return 0
    return catProjects.reduce((sum, p) => sum + p.roi, 0) / catProjects.length
  })

  roiChart = echarts.init(roiChartEl.value)
  roiChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: '{b}<br/>Average ROI: {c}%' },
    grid: { top: 30, left: 60, right: 20, bottom: 40, containLabel: true },
    xAxis: { type: 'category', data: categories, axisLabel: { rotate: 30, fontSize: 11 } },
    yAxis: { type: 'value', name: 'ROI (%)', min: 0, max: 30 },
    series: [{
      type: 'bar',
      data: rois,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const value = params.value
          if (value >= 20) return '#22c55e'
          if (value >= 12) return '#3b82f6'
          return '#f59e0b'
        }
      },
      label: { show: true, position: 'top', formatter: '{c}%' }
    }]
  })
}

const refreshCharts = () => {
  nextTick(() => {
    initForecastChart()
    initAllocationChart()
    initQuarterlyChart()
    initRoiChart()
  })
}

// ==================== Actions ====================
const viewProjectDetail = (project: CAPEXProject) => {
  selectedProject.value = project
  detailDialogVisible.value = true
}

const viewAllProjects = () => {
  ElMessage.info('Viewing all CAPEX projects')
}

const approveProject = (project: CAPEXProject | null) => {
  if (project) {
    ElMessage.success(`Project ${project.id} approved`)
  }
}

const rejectProject = (project: CAPEXProject | null) => {
  if (project) {
    ElMessage.warning(`Project ${project.id} rejected`)
  }
}

const updateStatus = (project: CAPEXProject | null) => {
  if (project) {
    ElMessage.success(`Status updated for ${project.id}`)
  }
}

const openBudgetDialog = () => {
  budgetDialogVisible.value = true
}

const saveBudget = () => {
  ElMessage.success(`Budget for ${budgetForm.value.year} created with total $${budgetForm.value.totalBudget.toLocaleString()}`)
  budgetDialogVisible.value = false
}

const exportData = () => {
  ElMessage.success('Exporting CAPEX data...')
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
    const charts = [forecastChart, allocationChart, quarterlyChart, roiChart]
    charts.forEach(chart => {
      if (chart && !chart.isDisposed()) chart.resize()
    })
  }, 100)
}

// ==================== Watch ====================
watch([searchText, categoryFilter, statusFilter, priorityFilter], () => {
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
  const charts = [forecastChart, allocationChart, quarterlyChart, roiChart]
  charts.forEach(chart => {
    if (chart && !chart.isDisposed()) chart.dispose()
  })
})
</script>

<style scoped>
.capex-planning-page {
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

/* Loading Screen - same as previous pages */
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

/* Project Detail */
.project-detail {
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

.milestone-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.milestone-title {
  font-weight: 600;
  font-size: 14px;
}

.milestone-status {
  display: inline-block;
  margin-top: 4px;
}

.milestone-description {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
}

.category-budget-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 300px;
  overflow-y: auto;
}

.category-budget-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background: #f8fafc;
  border-radius: 8px;
}

.category-name {
  font-size: 13px;
  font-weight: 500;
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
:deep(.el-timeline) {
  padding-left: 10px;
}
:deep(.el-timeline-item__wrapper) {
  padding-left: 28px;
}
</style>