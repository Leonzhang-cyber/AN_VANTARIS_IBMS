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
          <span class="loading-title">AI Recommendation Log</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">AI Decision Intelligence System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="ai-recommendation-log-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Cpu /></el-icon>
          AI Recommendation Log
        </h1>
        <div class="page-subtitle">Track and audit all AI-generated recommendations and decisions</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="exportLogs">
          <el-icon><Download /></el-icon> Export Logs
        </el-button>
        <el-button @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon> Refresh
        </el-button>
        <el-button type="danger" plain @click="clearFilters">
          <el-icon><Delete /></el-icon> Clear Filters
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue">
          <el-icon><Cpu /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalRecommendations }}</div>
          <div class="stat-label">Total Recommendations</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.adoptedCount }}</div>
          <div class="stat-label">Adopted</div>
          <div class="stat-trend up">Adoption Rate: {{ stats.adoptionRate }}%</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.pendingCount }}</div>
          <div class="stat-label">Pending Review</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.savingsGenerated }}<span class="stat-unit">k</span></div>
          <div class="stat-label">Savings Generated ($)</div>
          <div class="stat-trend up">↑ {{ stats.savingsGrowth }}% vs last month</div>
        </div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-select v-model="filters.category" placeholder="Category" clearable style="width: 140px" @change="applyFilters">
          <el-option label="Energy Optimization" value="energy" />
          <el-option label="Predictive Maintenance" value="maintenance" />
          <el-option label="Fault Detection" value="fault" />
          <el-option label="Cost Saving" value="cost" />
          <el-option label="ESG Compliance" value="esg" />
          <el-option label="Occupancy" value="occupancy" />
        </el-select>
        <el-select v-model="filters.status" placeholder="Status" clearable style="width: 130px" @change="applyFilters">
          <el-option label="Pending" value="pending" />
          <el-option label="Adopted" value="adopted" />
          <el-option label="Rejected" value="rejected" />
          <el-option label="In Progress" value="in_progress" />
        </el-select>
        <el-select v-model="filters.priority" placeholder="Priority" clearable style="width: 120px" @change="applyFilters">
          <el-option label="High" value="high" />
          <el-option label="Medium" value="medium" />
          <el-option label="Low" value="low" />
        </el-select>
        <el-select v-model="filters.confidence" placeholder="Confidence" clearable style="width: 140px" @change="applyFilters">
          <el-option label="High (>80%)" value="high" />
          <el-option label="Medium (60-80%)" value="medium" />
          <el-option label="Low (<60%)" value="low" />
        </el-select>
        <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="to"
            start-placeholder="Start Date"
            end-placeholder="End Date"
            size="default"
            style="width: 260px"
            @change="applyFilters"
        />
      </div>
      <div class="filter-right">
        <el-input v-model="searchKeyword" placeholder="Search recommendations..." style="width: 220px" clearable @clear="applyFilters" @keyup.enter="applyFilters">
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
    </div>

    <!-- Recommendations Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">
          <el-icon><List /></el-icon>
          AI Recommendation Log
        </span>
        <el-radio-group v-model="viewMode" size="small">
          <el-radio-button value="table">Table View</el-radio-button>
          <el-radio-button value="timeline">Timeline View</el-radio-button>
        </el-radio-group>
      </div>

      <!-- Table View -->
      <el-table :data="paginatedRecommendations" stripe style="width: 100%" v-loading="tableLoading" v-if="viewMode === 'table'">
        <el-table-column prop="timestamp" label="Timestamp" width="160" />
        <el-table-column prop="category" label="Category" width="140">
          <template #default="{ row }">
            <el-tag :type="getCategoryType(row.category)" size="small">{{ getCategoryLabel(row.category) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="Recommendation" min-width="250" />
        <el-table-column prop="priority" label="Priority" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)" size="small">{{ getPriorityLabel(row.priority) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="confidence" label="Confidence" width="120">
          <template #default="{ row }">
            <el-progress :percentage="row.confidence" :stroke-width="6" :show-text="false" />
            <span style="margin-left: 8px; font-size: 12px">{{ row.confidence }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="potentialSavings" label="Potential Savings" width="130">
          <template #default="{ row }">
            <span class="savings-value">${{ formatSavings(row.potentialSavings) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDetail(row)">Details</el-button>
            <el-button link type="success" size="small" @click="adoptRecommendation(row)" v-if="row.status === 'pending'">Adopt</el-button>
            <el-button link type="danger" size="small" @click="rejectRecommendation(row)" v-if="row.status === 'pending'">Reject</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Timeline View -->
      <div v-if="viewMode === 'timeline'" class="timeline-container">
        <div class="timeline" v-for="(group, year) in groupedByYear" :key="year">
          <div class="timeline-year">
            <span class="year-badge">{{ year }}</span>
          </div>
          <div v-for="(monthGroup, month) in group" :key="month" class="timeline-month">
            <div class="month-header">
              <span class="month-name">{{ month }}</span>
            </div>
            <div v-for="rec in monthGroup" :key="rec.id" class="timeline-item" :class="rec.status">
              <div class="timeline-dot" :class="rec.status"></div>
              <div class="timeline-content">
                <div class="timeline-header">
                  <span class="timeline-title">{{ rec.title }}</span>
                  <span class="timeline-date">{{ formatTime(rec.timestamp) }}</span>
                </div>
                <div class="timeline-body">
                  <p class="timeline-description">{{ rec.description }}</p>
                  <div class="timeline-meta">
                    <el-tag :type="getCategoryType(rec.category)" size="small">{{ getCategoryLabel(rec.category) }}</el-tag>
                    <el-tag :type="getPriorityType(rec.priority)" size="small">{{ getPriorityLabel(rec.priority) }}</el-tag>
                    <span class="confidence-badge">Confidence: {{ rec.confidence }}%</span>
                    <span class="savings-badge" v-if="rec.potentialSavings">Save: ${{ formatSavings(rec.potentialSavings) }}</span>
                  </div>
                  <div class="timeline-actions" v-if="rec.status === 'pending'">
                    <el-button size="small" type="success" @click="adoptRecommendation(rec)">Adopt</el-button>
                    <el-button size="small" type="danger" @click="rejectRecommendation(rec)">Reject</el-button>
                    <el-button size="small" @click="viewDetail(rec)">Details</el-button>
                  </div>
                  <div class="timeline-status" v-else>
                    <el-tag :type="getStatusType(rec.status)" size="small">{{ getStatusLabel(rec.status) }}</el-tag>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div class="pagination-container" v-if="viewMode === 'table'">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="filteredRecommendations.length"
            layout="total, sizes, prev, pager, next"
            background
        />
      </div>
    </div>

    <!-- Recommendation Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`Recommendation Details - ${selectedRecommendation?.title}`" width="700px">
      <div v-if="selectedRecommendation" class="recommendation-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="ID">{{ selectedRecommendation.id }}</el-descriptions-item>
          <el-descriptions-item label="Timestamp">{{ selectedRecommendation.timestamp }}</el-descriptions-item>
          <el-descriptions-item label="Category">
            <el-tag :type="getCategoryType(selectedRecommendation.category)" size="small">{{ getCategoryLabel(selectedRecommendation.category) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Priority">
            <el-tag :type="getPriorityType(selectedRecommendation.priority)" size="small">{{ getPriorityLabel(selectedRecommendation.priority) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Confidence">
            <el-progress :percentage="selectedRecommendation.confidence" :stroke-width="8" />
          </el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusType(selectedRecommendation.status)" size="small">{{ getStatusLabel(selectedRecommendation.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Potential Savings" v-if="selectedRecommendation.potentialSavings">
            ${{ formatSavings(selectedRecommendation.potentialSavings) }}
          </el-descriptions-item>
          <el-descriptions-item label="Implementation Cost" v-if="selectedRecommendation.implementationCost">
            ${{ formatSavings(selectedRecommendation.implementationCost) }}
          </el-descriptions-item>
          <el-descriptions-item label="ROI" v-if="selectedRecommendation.roi">
            {{ selectedRecommendation.roi }}%
          </el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ selectedRecommendation.description }}</el-descriptions-item>
          <el-descriptions-item label="AI Model" :span="2">{{ selectedRecommendation.aiModel }}</el-descriptions-item>
          <el-descriptions-item label="Decision Logic" :span="2">{{ selectedRecommendation.decisionLogic }}</el-descriptions-item>
          <el-descriptions-item label="Supporting Data" :span="2">
            <div class="supporting-data">
              <div v-for="(data, idx) in selectedRecommendation.supportingData" :key="idx" class="data-point">
                • {{ data }}
              </div>
            </div>
          </el-descriptions-item>
        </el-descriptions>

        <div class="detail-actions" v-if="selectedRecommendation.status === 'pending'">
          <el-button type="success" @click="adoptRecommendation(selectedRecommendation)">Adopt Recommendation</el-button>
          <el-button type="danger" @click="rejectRecommendation(selectedRecommendation)">Reject</el-button>
          <el-button @click="scheduleReview(selectedRecommendation)">Schedule Review</el-button>
        </div>
        <div class="detail-actions" v-else-if="selectedRecommendation.status === 'adopted'">
          <el-button type="primary" @click="trackImplementation(selectedRecommendation)">Track Implementation</el-button>
          <el-button @click="viewEvidence(selectedRecommendation)">View Evidence</el-button>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="exportRecommendation" v-if="selectedRecommendation">Export</el-button>
      </template>
    </el-dialog>

    <!-- Adopt Confirmation Dialog -->
    <el-dialog v-model="adoptDialogVisible" title="Adopt Recommendation" width="500px">
      <el-form :model="adoptForm" label-width="120px">
        <el-form-item label="Implementation Plan">
          <el-input type="textarea" v-model="adoptForm.implementationPlan" rows="3" placeholder="Describe implementation plan..." />
        </el-form-item>
        <el-form-item label="Assigned To">
          <el-select v-model="adoptForm.assignedTo" placeholder="Select assignee" style="width: 100%">
            <el-option v-for="staff in staffList" :key="staff.id" :label="staff.name" :value="staff.name" />
          </el-select>
        </el-form-item>
        <el-form-item label="Target Date">
          <el-date-picker v-model="adoptForm.targetDate" type="date" placeholder="Select target date" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Notes">
          <el-input type="textarea" v-model="adoptForm.notes" rows="2" placeholder="Additional notes..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="adoptDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmAdopt">Confirm Adoption</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Cpu, Download, Refresh, Delete, CircleCheck, Clock,
  TrendCharts, List, Search
} from '@element-plus/icons-vue'

// ==================== Types ====================
interface AIRecommendation {
  id: string
  timestamp: string
  category: 'energy' | 'maintenance' | 'fault' | 'cost' | 'esg' | 'occupancy'
  title: string
  description: string
  priority: 'high' | 'medium' | 'low'
  confidence: number
  status: 'pending' | 'adopted' | 'rejected' | 'in_progress'
  potentialSavings?: number
  implementationCost?: number
  roi?: number
  aiModel: string
  decisionLogic: string
  supportingData: string[]
  adoptedBy?: string
  adoptedAt?: string
}

interface Staff {
  id: string
  name: string
  role: string
}

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading AI recommendation logs...')
const refreshing = ref(false)

const loadingMessages = [
  'Loading AI recommendation logs...',
  'Fetching decision records...',
  'Analyzing adoption metrics...',
  'Loading AI model data...',
  'Almost ready...'
]

// ==================== Mock Data ====================
const staffList: Staff[] = [
  { id: 'STF001', name: 'John Smith', role: 'Facility Manager' },
  { id: 'STF002', name: 'Sarah Johnson', role: 'Energy Analyst' },
  { id: 'STF003', name: 'Mike Wilson', role: 'Maintenance Lead' },
  { id: 'STF004', name: 'Emma Davis', role: 'Operations Manager' },
  { id: 'STF005', name: 'David Brown', role: 'Sustainability Officer' }
]

const generateRecommendations = (): AIRecommendation[] => {
  const recommendations: AIRecommendation[] = []

  const titles = {
    energy: ['Optimize HVAC Schedule', 'Adjust Lighting Setpoints', 'Peak Load Shifting', 'Chiller Efficiency Improvement'],
    maintenance: ['Predictive Maintenance for AHU', 'Filter Replacement Alert', 'Bearing Wear Detection', 'Belt Tension Adjustment'],
    fault: ['Chiller Fault Detected', 'VFD Anomaly Alert', 'Sensor Drift Correction', 'Communication Error Resolution'],
    cost: ['Energy Tariff Optimization', 'Demand Response Participation', 'Equipment Replacement ROI', 'Utility Rebate Opportunity'],
    esg: ['Carbon Reduction Strategy', 'Water Conservation Alert', 'Waste Diversion Recommendation', 'Renewable Energy Integration'],
    occupancy: ['Space Utilization Optimization', 'Zoning Adjustment', 'Peak Hour Staffing', 'Meeting Room Reconfiguration']
  }

  const statuses: AIRecommendation['status'][] = ['pending', 'adopted', 'rejected', 'in_progress']
  const priorities: AIRecommendation['priority'][] = ['high', 'medium', 'low']
  const categories: AIRecommendation['category'][] = ['energy', 'maintenance', 'fault', 'cost', 'esg', 'occupancy']

  for (let i = 0; i < 120; i++) {
    const category = categories[Math.floor(Math.random() * categories.length)]
    const title = titles[category][Math.floor(Math.random() * titles[category].length)]
    const status = statuses[Math.floor(Math.random() * statuses.length)]
    const priority = priorities[Math.floor(Math.random() * priorities.length)]
    const confidence = 55 + Math.floor(Math.random() * 40)

    const timestamp = new Date(Date.now() - Math.random() * 90 * 24 * 60 * 60 * 1000)

    const potentialSavings = Math.floor(Math.random() * 50000) / 1000
    const implementationCost = Math.floor(Math.random() * 20000) / 1000
    const roi = potentialSavings > 0 && implementationCost > 0
        ? Math.floor((potentialSavings / implementationCost) * 100)
        : undefined

    recommendations.push({
      id: `AI-REC-${String(i + 1).padStart(5, '0')}`,
      timestamp: timestamp.toISOString().slice(0, 16).replace('T', ' '),
      category,
      title,
      description: `AI model detected an opportunity to ${title.toLowerCase()} which could result in significant improvements. Recommended action based on historical data analysis and real-time sensor readings.`,
      priority,
      confidence,
      status,
      potentialSavings,
      implementationCost,
      roi: roi && roi > 0 ? roi : undefined,
      aiModel: `GPT-4 ${category.charAt(0).toUpperCase() + category.slice(1)} Optimizer v2.1`,
      decisionLogic: `Based on analysis of ${Math.floor(Math.random() * 30) + 10} data points including historical patterns, real-time metrics, and predictive models.`,
      supportingData: [
        `Historical ${category} data from past 90 days`,
        `Real-time sensor readings from ${Math.floor(Math.random() * 20) + 5} devices`,
        `Benchmark comparison against similar facilities`,
        `${Math.floor(Math.random() * 10) + 1} similar successful implementations`
      ],
      adoptedBy: status !== 'pending' ? staffList[Math.floor(Math.random() * staffList.length)].name : undefined,
      adoptedAt: status !== 'pending' ? new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 16).replace('T', ' ') : undefined
    })
  }

  return recommendations.sort((a, b) => b.timestamp.localeCompare(a.timestamp))
}

const recommendations = ref<AIRecommendation[]>(generateRecommendations())

// ==================== State ====================
const viewMode = ref<'table' | 'timeline'>('table')
const searchKeyword = ref('')
const dateRange = ref<Date[] | null>(null)
const filters = ref({
  category: '',
  status: '',
  priority: '',
  confidence: ''
})
const currentPage = ref(1)
const pageSize = ref(20)
const detailDialogVisible = ref(false)
const adoptDialogVisible = ref(false)
const selectedRecommendation = ref<AIRecommendation | null>(null)
const tableLoading = ref(false)

const adoptForm = ref({
  implementationPlan: '',
  assignedTo: '',
  targetDate: null as Date | null,
  notes: ''
})

// ==================== Computed ====================
const stats = computed(() => {
  const total = recommendations.value.length
  const adopted = recommendations.value.filter(r => r.status === 'adopted').length
  const pending = recommendations.value.filter(r => r.status === 'pending').length
  const inProgress = recommendations.value.filter(r => r.status === 'in_progress').length
  const adoptionRate = total > 0 ? Math.round((adopted / total) * 100) : 0

  const totalSavings = recommendations.value
      .filter(r => r.status === 'adopted' && r.potentialSavings)
      .reduce((acc, r) => acc + (r.potentialSavings || 0), 0)

  return {
    totalRecommendations: total,
    adoptedCount: adopted,
    pendingCount: pending,
    inProgressCount: inProgress,
    adoptionRate,
    savingsGenerated: totalSavings.toFixed(1),
    savingsGrowth: 12
  }
})

const filteredRecommendations = computed(() => {
  let filtered = [...recommendations.value]

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(r =>
        r.title.toLowerCase().includes(keyword) ||
        r.description.toLowerCase().includes(keyword) ||
        r.id.toLowerCase().includes(keyword)
    )
  }

  if (filters.value.category) {
    filtered = filtered.filter(r => r.category === filters.value.category)
  }

  if (filters.value.status) {
    filtered = filtered.filter(r => r.status === filters.value.status)
  }

  if (filters.value.priority) {
    filtered = filtered.filter(r => r.priority === filters.value.priority)
  }

  if (filters.value.confidence) {
    if (filters.value.confidence === 'high') {
      filtered = filtered.filter(r => r.confidence >= 80)
    } else if (filters.value.confidence === 'medium') {
      filtered = filtered.filter(r => r.confidence >= 60 && r.confidence < 80)
    } else if (filters.value.confidence === 'low') {
      filtered = filtered.filter(r => r.confidence < 60)
    }
  }

  if (dateRange.value && dateRange.value.length === 2) {
    const [start, end] = dateRange.value
    filtered = filtered.filter(r => {
      const recDate = new Date(r.timestamp)
      return recDate >= start && recDate <= end
    })
  }

  return filtered
})

const paginatedRecommendations = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredRecommendations.value.slice(start, end)
})

const groupedByYear = computed(() => {
  const groups: Record<string, Record<string, AIRecommendation[]>> = {}

  for (const rec of filteredRecommendations.value) {
    const date = new Date(rec.timestamp)
    const year = date.getFullYear().toString()
    const month = date.toLocaleString('default', { month: 'long' })

    if (!groups[year]) groups[year] = {}
    if (!groups[year][month]) groups[year][month] = []
    groups[year][month].push(rec)
  }

  return groups
})

// ==================== Helper Functions ====================
const getCategoryType = (category: string) => {
  const map: Record<string, string> = {
    energy: 'success', maintenance: 'warning', fault: 'danger',
    cost: 'info', esg: 'primary', occupancy: ''
  }
  return map[category] || 'info'
}

const getCategoryLabel = (category: string) => {
  const map: Record<string, string> = {
    energy: 'Energy Optimization', maintenance: 'Predictive Maintenance',
    fault: 'Fault Detection', cost: 'Cost Saving', esg: 'ESG Compliance',
    occupancy: 'Occupancy'
  }
  return map[category] || category
}

const getPriorityType = (priority: string) => {
  const map: Record<string, string> = { high: 'danger', medium: 'warning', low: 'info' }
  return map[priority] || 'info'
}

const getPriorityLabel = (priority: string) => {
  const map: Record<string, string> = { high: 'High', medium: 'Medium', low: 'Low' }
  return map[priority] || priority
}

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    pending: 'warning', adopted: 'success', rejected: 'danger', in_progress: 'primary'
  }
  return map[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    pending: 'Pending', adopted: 'Adopted', rejected: 'Rejected', in_progress: 'In Progress'
  }
  return map[status] || status
}

const formatSavings = (savings?: number) => {
  if (!savings) return '0'
  if (savings >= 1000) return `${(savings / 1000).toFixed(1)}k`
  return savings.toFixed(1)
}

const formatTime = (timestamp: string) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const applyFilters = () => {
  currentPage.value = 1
}

const clearFilters = () => {
  searchKeyword.value = ''
  dateRange.value = null
  filters.value = { category: '', status: '', priority: '', confidence: '' }
  currentPage.value = 1
  ElMessage.success('Filters cleared')
}

const viewDetail = (rec: AIRecommendation) => {
  selectedRecommendation.value = rec
  detailDialogVisible.value = true
}

const adoptRecommendation = (rec: AIRecommendation) => {
  selectedRecommendation.value = rec
  adoptForm.value = { implementationPlan: '', assignedTo: '', targetDate: null, notes: '' }
  adoptDialogVisible.value = true
}

const confirmAdopt = () => {
  if (!selectedRecommendation.value) return

  const index = recommendations.value.findIndex(r => r.id === selectedRecommendation.value!.id)
  if (index !== -1) {
    recommendations.value[index].status = 'adopted'
    recommendations.value[index].adoptedBy = adoptForm.value.assignedTo || 'System Admin'
    recommendations.value[index].adoptedAt = new Date().toISOString().slice(0, 16).replace('T', ' ')
    ElMessage.success(`Recommendation ${selectedRecommendation.value.id} adopted successfully`)
  }
  adoptDialogVisible.value = false
  detailDialogVisible.value = false
}

const rejectRecommendation = (rec: AIRecommendation) => {
  ElMessageBox.confirm(`Reject recommendation "${rec.title}"?`, 'Confirm Rejection', {
    confirmButtonText: 'Yes, Reject',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    const index = recommendations.value.findIndex(r => r.id === rec.id)
    if (index !== -1) {
      recommendations.value[index].status = 'rejected'
      ElMessage.success(`Recommendation ${rec.id} rejected`)
    }
    detailDialogVisible.value = false
  }).catch(() => {})
}

const scheduleReview = (rec: AIRecommendation) => {
  ElMessage.info(`Review scheduled for ${rec.title}`)
}

const trackImplementation = (rec: AIRecommendation) => {
  ElMessage.info(`Tracking implementation for ${rec.title}`)
}

const viewEvidence = (rec: AIRecommendation) => {
  ElMessage.info(`Viewing evidence for ${rec.title}`)
}

const exportRecommendation = () => {
  ElMessage.success('Exporting recommendation details...')
}

const exportLogs = () => {
  ElMessage.success('Exporting logs...')
  setTimeout(() => {
    ElMessage.success('Logs exported successfully')
  }, 1000)
}

const refreshData = async () => {
  refreshing.value = true
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 800))
  recommendations.value = generateRecommendations()
  refreshing.value = false
  tableLoading.value = false
  ElMessage.success('Data refreshed')
}

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
    }, 500)
  }, 2200)
}

onMounted(() => {
  startLoading()
})
</script>

<style scoped>
.ai-recommendation-log-page {
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
.stat-trend.down { color: #ef4444; }

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
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.savings-value {
  font-weight: 600;
  color: #22c55e;
}

/* Timeline View */
.timeline-container {
  max-height: 600px;
  overflow-y: auto;
  padding: 10px;
}

.timeline-year {
  margin: 20px 0 10px;
}

.year-badge {
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
}

.timeline-month {
  margin: 16px 0 0 20px;
}

.month-header {
  margin-bottom: 12px;
}

.month-name {
  font-size: 16px;
  font-weight: 600;
  color: #64748b;
  border-left: 3px solid #3b82f6;
  padding-left: 12px;
}

.timeline-item {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  position: relative;
}

.timeline-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-top: 4px;
  flex-shrink: 0;
}

.timeline-dot.pending { background: #f59e0b; box-shadow: 0 0 0 3px #fef3c7; }
.timeline-dot.adopted { background: #22c55e; box-shadow: 0 0 0 3px #dcfce7; }
.timeline-dot.rejected { background: #ef4444; box-shadow: 0 0 0 3px #fee2e2; }
.timeline-dot.in_progress { background: #3b82f6; box-shadow: 0 0 0 3px #eef2ff; }

.timeline-content {
  flex: 1;
  background: #f8fafc;
  border-radius: 12px;
  padding: 12px 16px;
  transition: all 0.2s;
}

.timeline-content:hover {
  background: #f1f5f9;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  flex-wrap: wrap;
  gap: 8px;
}

.timeline-title {
  font-weight: 600;
  font-size: 14px;
  color: #1e293b;
}

.timeline-date {
  font-size: 11px;
  color: #94a3b8;
}

.timeline-description {
  font-size: 12px;
  color: #475569;
  margin: 8px 0;
  line-height: 1.4;
}

.timeline-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin: 8px 0;
}

.confidence-badge, .savings-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 12px;
  background: #e2e8f0;
  color: #475569;
}

.savings-badge {
  background: #dcfce7;
  color: #166534;
}

.timeline-actions, .timeline-status {
  margin-top: 8px;
  display: flex;
  gap: 8px;
}

/* Recommendation Detail */
.recommendation-detail {
  padding: 8px;
}

.supporting-data {
  padding: 8px 0;
}

.data-point {
  font-size: 12px;
  color: #475569;
  padding: 4px 0;
}

.detail-actions {
  margin-top: 20px;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

/* Responsive */
@media (max-width: 1000px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
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
  .timeline-header {
    flex-direction: column;
    align-items: flex-start;
  }
}

/* Element Plus Overrides */
:deep(.el-table) {
  border-radius: 12px;
  overflow: hidden;
}
:deep(.el-table th.el-table__cell) {
  background-color: #f8fafc !important;
  color: #334155;
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
  padding: 20px;
}
:deep(.el-progress-bar__inner) {
  border-radius: 4px;
}
</style>