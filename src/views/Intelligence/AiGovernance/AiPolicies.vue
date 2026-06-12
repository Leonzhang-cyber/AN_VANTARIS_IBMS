<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import * as echarts from 'echarts'
import {
  Refresh, Setting, User, Clock,
  Warning, CircleCheck, TrendCharts, DataLine,
  Star, Share, CopyDocument, Delete, Mic,
  Picture, Document, Upload, Download,
  MagicStick, ChatDotRound, Message, Service,
  Search, Edit, Plus, VideoPlay, VideoPause,
  Operation, Headset, Monitor, Cpu, Connection,
  Lock, Key, Shield, Medal, Flag
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Loading AI governance policies...',
  'Analyzing compliance status...',
  'Preparing policy framework...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedStatus = ref('all')
const selectedCategory = ref('all')
const detailsVisible = ref(false)
const createPolicyVisible = ref(false)
const editPolicyVisible = ref(false)
const chartRef = ref(null)

let complianceChart: echarts.ECharts | null = null

// Status filters
const statusOptions = [
  { value: 'all', label: 'All Status' },
  { value: 'active', label: 'Active', color: '#67C23A' },
  { value: 'draft', label: 'Draft', color: '#E6A23C' },
  { value: 'review', label: 'Under Review', color: '#409EFF' },
  { value: 'archived', label: 'Archived', color: '#909399' }
]

// Category filters
const categoryOptions = [
  { value: 'all', label: 'All Categories' },
  { value: 'data', label: 'Data Governance' },
  { value: 'ethics', label: 'AI Ethics' },
  { value: 'security', label: 'Security' },
  { value: 'compliance', label: 'Compliance' },
  { value: 'operations', label: 'Operations' }
]

// AI Policies data
const policies = ref([
  {
    id: 'POL001', name: 'Data Privacy & Protection Policy', category: 'data',
    description: 'Governs collection, storage, and processing of personal and sensitive data by AI systems',
    status: 'active', version: '2.1.0', effectiveDate: '2024-01-01',
    lastReviewed: '2024-01-15', nextReview: '2025-01-01', owner: 'Data Governance Team',
    compliance: 98, controls: 12, violations: 2
  },
  {
    id: 'POL002', name: 'AI Ethics & Fairness Policy', category: 'ethics',
    description: 'Ensures AI systems operate without bias and maintain fairness across all user groups',
    status: 'active', version: '1.5.0', effectiveDate: '2023-12-01',
    lastReviewed: '2023-12-10', nextReview: '2024-12-01', owner: 'AI Ethics Committee',
    compliance: 95, controls: 8, violations: 1
  },
  {
    id: 'POL003', name: 'Model Security & Access Control', category: 'security',
    description: 'Defines security requirements for AI model deployment and access management',
    status: 'active', version: '3.0.0', effectiveDate: '2024-01-10',
    lastReviewed: '2024-01-20', nextReview: '2025-01-10', owner: 'Security Team',
    compliance: 99, controls: 15, violations: 0
  },
  {
    id: 'POL004', name: 'Regulatory Compliance Framework', category: 'compliance',
    description: 'Ensures AI systems comply with GDPR, CCPA, and other relevant regulations',
    status: 'draft', version: '1.0.0', effectiveDate: null,
    lastReviewed: '2024-01-05', nextReview: null, owner: 'Legal & Compliance',
    compliance: 75, controls: 10, violations: 3
  },
  {
    id: 'POL005', name: 'AI Model Lifecycle Management', category: 'operations',
    description: 'Governs development, testing, deployment, and retirement of AI models',
    status: 'active', version: '2.0.0', effectiveDate: '2023-11-15',
    lastReviewed: '2023-11-20', nextReview: '2024-11-15', owner: 'ML Ops Team',
    compliance: 96, controls: 14, violations: 1
  },
  {
    id: 'POL006', name: 'Algorithm Transparency Policy', category: 'ethics',
    description: 'Requires documentation and explainability of AI decision-making processes',
    status: 'review', version: '1.2.0', effectiveDate: null,
    lastReviewed: '2024-01-18', nextReview: null, owner: 'AI Ethics Committee',
    compliance: 82, controls: 6, violations: 2
  },
  {
    id: 'POL007', name: 'Third-Party AI Integration', category: 'security',
    description: 'Security and compliance requirements for integrating third-party AI services',
    status: 'active', version: '1.8.0', effectiveDate: '2023-12-10',
    lastReviewed: '2023-12-15', nextReview: '2024-12-10', owner: 'Security Team',
    compliance: 94, controls: 9, violations: 1
  },
  {
    id: 'POL008', name: 'Data Retention & Disposal', category: 'data',
    description: 'Specifies retention periods and secure disposal methods for training data',
    status: 'active', version: '2.2.0', effectiveDate: '2024-01-05',
    lastReviewed: '2024-01-12', nextReview: '2025-01-05', owner: 'Data Governance Team',
    compliance: 97, controls: 11, violations: 0
  }
])

// Policy statistics
const policyStats = reactive({
  total: 0,
  active: 0,
  draft: 0,
  review: 0,
  archived: 0,
  avgCompliance: 0,
  totalControls: 0,
  totalViolations: 0
})

// Create policy form
const createPolicyForm = reactive({
  name: '',
  category: 'data',
  description: '',
  owner: '',
  version: '1.0.0'
})

// Edit policy form
const editPolicyForm = reactive({
  id: '',
  name: '',
  category: '',
  description: '',
  status: '',
  version: '',
  owner: ''
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 8,
  total: policies.value.length
})

// Filtered policies
const filteredPolicies = computed(() => {
  let filtered = policies.value
  if (searchKeyword.value) {
    filtered = filtered.filter(p =>
        p.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        p.id.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        p.description.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (selectedStatus.value !== 'all') {
    filtered = filtered.filter(p => p.status === selectedStatus.value)
  }
  if (selectedCategory.value !== 'all') {
    filtered = filtered.filter(p => p.category === selectedCategory.value)
  }
  pagination.total = filtered.length
  const start = (pagination.page - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return filtered.slice(start, end)
})

// Compliance data for chart
const complianceData = computed(() => {
  return policies.value.map(p => ({
    name: p.name.substring(0, 20) + (p.name.length > 20 ? '...' : ''),
    compliance: p.compliance
  }))
})

// ==================== Loading Simulation ====================
onMounted(() => {
  let messageIndex = 0

  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 600)

  const progressInterval = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 12 + 4
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
        initChart()
        updateStats()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2500)
})

// ==================== Chart Functions ====================
const initChart = () => {
  if (!chartRef.value) return

  complianceChart = echarts.init(chartRef.value)
  complianceChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['Compliance Score (%)'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: complianceData.value.map(c => c.name), axisLabel: { rotate: 30, interval: 0 } },
    yAxis: { type: 'value', name: 'Compliance Score (%)', min: 0, max: 100 },
    series: [{
      name: 'Compliance Score (%)',
      type: 'bar',
      data: complianceData.value.map(c => c.compliance),
      itemStyle: {
        color: (params: any) => {
          const value = params.value
          if (value >= 90) return '#67C23A'
          if (value >= 75) return '#E6A23C'
          return '#F56C6C'
        },
        borderRadius: [4, 4, 0, 0]
      },
      label: { show: true, position: 'top', formatter: '{c}%' }
    }]
  })
}

const updateStats = () => {
  policyStats.total = policies.value.length
  policyStats.active = policies.value.filter(p => p.status === 'active').length
  policyStats.draft = policies.value.filter(p => p.status === 'draft').length
  policyStats.review = policies.value.filter(p => p.status === 'review').length
  policyStats.archived = policies.value.filter(p => p.status === 'archived').length
  policyStats.avgCompliance = Math.round(policies.value.reduce((sum, p) => sum + p.compliance, 0) / policies.value.length)
  policyStats.totalControls = policies.value.reduce((sum, p) => sum + p.controls, 0)
  policyStats.totalViolations = policies.value.reduce((sum, p) => sum + p.violations, 0)
}

const handleResize = () => {
  complianceChart?.resize()
}

// ==================== Policy Functions ====================
const refreshPolicies = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  updateStats()
  loading.value = false
  ElMessage.success('Policies refreshed successfully')
}

const viewPolicyDetails = (policy: any) => {
  selectedPolicy.value = policy
  detailsVisible.value = true
}

const editPolicy = (policy: any) => {
  editPolicyForm.id = policy.id
  editPolicyForm.name = policy.name
  editPolicyForm.category = policy.category
  editPolicyForm.description = policy.description
  editPolicyForm.status = policy.status
  editPolicyForm.version = policy.version
  editPolicyForm.owner = policy.owner
  editPolicyVisible.value = true
}

const savePolicyEdit = async () => {
  if (!editPolicyForm.name) {
    ElMessage.warning('Please enter a policy name')
    return
  }

  await new Promise(resolve => setTimeout(resolve, 1000))

  const index = policies.value.findIndex(p => p.id === editPolicyForm.id)
  if (index !== -1) {
    policies.value[index] = {
      ...policies.value[index],
      name: editPolicyForm.name,
      category: editPolicyForm.category,
      description: editPolicyForm.description,
      status: editPolicyForm.status,
      version: editPolicyForm.version,
      owner: editPolicyForm.owner,
      lastReviewed: new Date().toISOString().split('T')[0]
    }
  }

  updateStats()
  editPolicyVisible.value = false
  ElMessage.success('Policy updated successfully')
}

const deletePolicy = async (policy: any) => {
  await ElMessageBox.confirm(
      `Delete policy "${policy.name}"? This action cannot be undone.`,
      'Confirm Delete',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'danger'
      }
  )

  const index = policies.value.findIndex(p => p.id === policy.id)
  if (index !== -1) {
    policies.value.splice(index, 1)
  }

  updateStats()
  initChart()
  ElMessage.success('Policy deleted successfully')
}

const openCreatePolicy = () => {
  createPolicyForm.name = ''
  createPolicyForm.category = 'data'
  createPolicyForm.description = ''
  createPolicyForm.owner = ''
  createPolicyForm.version = '1.0.0'
  createPolicyVisible.value = true
}

const createPolicy = async () => {
  if (!createPolicyForm.name) {
    ElMessage.warning('Please enter a policy name')
    return
  }

  if (!createPolicyForm.owner) {
    ElMessage.warning('Please enter an owner')
    return
  }

  await new Promise(resolve => setTimeout(resolve, 1000))

  const newPolicy = {
    id: `POL${String(policies.value.length + 1).padStart(3, '0')}`,
    name: createPolicyForm.name,
    category: createPolicyForm.category,
    description: createPolicyForm.description || 'New policy',
    status: 'draft',
    version: createPolicyForm.version,
    effectiveDate: null,
    lastReviewed: new Date().toISOString().split('T')[0],
    nextReview: null,
    owner: createPolicyForm.owner,
    compliance: 0,
    controls: 0,
    violations: 0
  }

  policies.value.unshift(newPolicy)
  updateStats()
  initChart()
  createPolicyVisible.value = false
  ElMessage.success('Policy created successfully')
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.page = 1
}

const handlePageChange = (val: number) => {
  pagination.page = val
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'active': return 'success'
    case 'draft': return 'warning'
    case 'review': return 'primary'
    case 'archived': return 'info'
    default: return 'info'
  }
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'active': return CircleCheck
    case 'draft': return Edit
    case 'review': return Clock
    case 'archived': return Delete
    default: return Clock
  }
}

const getCategoryIcon = (category: string) => {
  switch (category) {
    case 'data': return '📊'
    case 'ethics': return '⚖️'
    case 'security': return '🔒'
    case 'compliance': return '📋'
    case 'operations': return '⚙️'
    default: return '📄'
  }
}

const getComplianceColor = (score: number) => {
  if (score >= 90) return '#67C23A'
  if (score >= 75) return '#E6A23C'
  return '#F56C6C'
}

const selectedPolicy = ref<any>(null)
</script>

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
          <span class="loading-title">Loading AI Policies</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">AI Governance - AI Policies</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="ai-policies-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">AI Policies</h1>
        <p class="page-subtitle">Governance framework for responsible AI development and deployment</p>
      </div>
      <div class="header-right">
        <el-button type="primary" size="large" @click="openCreatePolicy">
          <el-icon><Plus /></el-icon>
          Create Policy
        </el-button>
        <el-button size="large" @click="refreshPolicies" :loading="loading">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Stats Cards Row -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon total-icon">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ policyStats.total }}</div>
          <div class="stat-label">Total Policies</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ policyStats.active }} Active</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon compliance-icon">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ policyStats.avgCompliance }}%</div>
          <div class="stat-label">Avg Compliance</div>
        </div>
        <div class="stat-trend">
          <el-progress :percentage="policyStats.avgCompliance" :stroke-width="4" :show-text="false" />
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon controls-icon">
          <el-icon><Lock /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ policyStats.totalControls }}</div>
          <div class="stat-label">Active Controls</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">+12 this quarter</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon violations-icon">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ policyStats.totalViolations }}</div>
          <div class="stat-label">Violations</div>
        </div>
        <div class="stat-trend">
          <span class="trend-down">-5 from last month</span>
        </div>
      </div>
    </div>

    <!-- Compliance Chart -->
    <div class="chart-section">
      <div class="section-header">
        <h3>Policy Compliance Scores</h3>
        <el-button text type="primary" @click="initChart">Refresh</el-button>
      </div>
      <div ref="chartRef" class="compliance-chart" style="height: 320px"></div>
    </div>

    <!-- Filters Bar -->
    <div class="filters-bar">
      <div class="filters-left">
        <div class="search-box">
          <el-input
              v-model="searchKeyword"
              placeholder="Search policies..."
              :prefix-icon="Search"
              clearable
              style="width: 240px"
          />
        </div>
        <div class="status-filters">
          <button
              v-for="s in statusOptions"
              :key="s.value"
              class="status-chip"
              :class="{ active: selectedStatus === s.value }"
              @click="selectedStatus = s.value"
          >
            <span class="chip-dot" :style="{ background: s.color }"></span>
            <span>{{ s.label }}</span>
          </button>
        </div>
      </div>
      <div class="filters-right">
        <el-select v-model="selectedCategory" placeholder="Category" clearable style="width: 160px">
          <el-option v-for="c in categoryOptions.slice(1)" :key="c.value" :label="c.label" :value="c.value" />
        </el-select>
      </div>
    </div>

    <!-- Policies Grid -->
    <div class="policies-grid">
      <div
          v-for="policy in filteredPolicies"
          :key="policy.id"
          class="policy-card"
      >
        <!-- Card Header -->
        <div class="card-header">
          <div class="policy-category">
            <span class="category-icon">{{ getCategoryIcon(policy.category) }}</span>
            <span class="category-name">{{ policy.category.toUpperCase() }}</span>
          </div>
          <div class="policy-status">
            <el-tag :type="getStatusType(policy.status)" size="small" effect="light">
              <el-icon><component :is="getStatusIcon(policy.status)" /></el-icon>
              {{ policy.status.toUpperCase() }}
            </el-tag>
          </div>
        </div>

        <!-- Card Body -->
        <div class="card-body">
          <h4 class="policy-name">{{ policy.name }}</h4>
          <p class="policy-description">{{ policy.description }}</p>

          <!-- Compliance Score -->
          <div class="compliance-section">
            <div class="compliance-header">
              <span>Compliance Score</span>
              <span class="compliance-value" :style="{ color: getComplianceColor(policy.compliance) }">
                {{ policy.compliance }}%
              </span>
            </div>
            <div class="compliance-bar">
              <div class="bar-fill" :style="{ width: policy.compliance + '%', background: getComplianceColor(policy.compliance) }"></div>
            </div>
          </div>

          <!-- Key Metrics -->
          <div class="key-metrics">
            <div class="metric">
              <span class="metric-label">Version</span>
              <span class="metric-value">{{ policy.version }}</span>
            </div>
            <div class="metric">
              <span class="metric-label">Controls</span>
              <span class="metric-value">{{ policy.controls }}</span>
            </div>
            <div class="metric">
              <span class="metric-label">Violations</span>
              <span class="metric-value" :class="{ 'has-violations': policy.violations > 0 }">
                {{ policy.violations }}
              </span>
            </div>
          </div>

          <!-- Dates -->
          <div class="dates">
            <div class="date-item">
              <span class="date-label">Effective:</span>
              <span class="date-value">{{ policy.effectiveDate || 'Not set' }}</span>
            </div>
            <div class="date-item">
              <span class="date-label">Next Review:</span>
              <span class="date-value">{{ policy.nextReview || 'Not scheduled' }}</span>
            </div>
          </div>

          <!-- Owner -->
          <div class="owner">
            <el-icon><User /></el-icon>
            <span>{{ policy.owner }}</span>
          </div>
        </div>

        <!-- Card Footer -->
        <div class="card-footer">
          <div class="last-reviewed">
            Last reviewed: {{ policy.lastReviewed }}
          </div>
          <div class="card-actions">
            <el-button size="small" @click="viewPolicyDetails(policy)">Details</el-button>
            <el-button size="small" type="primary" @click="editPolicy(policy)">Edit</el-button>
            <el-button size="small" type="danger" @click="deletePolicy(policy)">Delete</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredPolicies.length === 0" class="empty-state">
      <el-empty description="No policies found">
        <el-button type="primary" @click="openCreatePolicy">Create Policy</el-button>
      </el-empty>
    </div>

    <!-- Pagination -->
    <div v-if="filteredPolicies.length > 0" class="pagination-wrapper">
      <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[8, 12, 16, 24]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
      />
    </div>

    <!-- Policy Details Dialog -->
    <el-dialog v-model="detailsVisible" :title="selectedPolicy?.name" width="650px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Policy ID">{{ selectedPolicy?.id }}</el-descriptions-item>
        <el-descriptions-item label="Version">{{ selectedPolicy?.version }}</el-descriptions-item>
        <el-descriptions-item label="Category">{{ selectedPolicy?.category?.toUpperCase() }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusType(selectedPolicy?.status)" size="small">
            {{ selectedPolicy?.status?.toUpperCase() }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Owner">{{ selectedPolicy?.owner }}</el-descriptions-item>
        <el-descriptions-item label="Compliance Score">{{ selectedPolicy?.compliance }}%</el-descriptions-item>
        <el-descriptions-item label="Controls">{{ selectedPolicy?.controls }}</el-descriptions-item>
        <el-descriptions-item label="Violations">{{ selectedPolicy?.violations }}</el-descriptions-item>
        <el-descriptions-item label="Effective Date">{{ selectedPolicy?.effectiveDate || 'Not set' }}</el-descriptions-item>
        <el-descriptions-item label="Last Reviewed">{{ selectedPolicy?.lastReviewed }}</el-descriptions-item>
        <el-descriptions-item label="Next Review">{{ selectedPolicy?.nextReview || 'Not scheduled' }}</el-descriptions-item>
        <el-descriptions-item label="Description" :span="2">{{ selectedPolicy?.description }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailsVisible = false">Close</el-button>
        <el-button type="primary" @click="editPolicy(selectedPolicy)">Edit Policy</el-button>
      </template>
    </el-dialog>

    <!-- Create Policy Dialog -->
    <el-dialog v-model="createPolicyVisible" title="Create New Policy" width="550px">
      <el-form :model="createPolicyForm" label-width="120px">
        <el-form-item label="Policy Name" required>
          <el-input v-model="createPolicyForm.name" placeholder="Enter policy name" />
        </el-form-item>
        <el-form-item label="Category">
          <el-select v-model="createPolicyForm.category" style="width: 100%">
            <el-option v-for="c in categoryOptions.slice(1)" :key="c.value" :label="c.label" :value="c.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="createPolicyForm.description" type="textarea" rows="2" placeholder="Enter description" />
        </el-form-item>
        <el-form-item label="Owner" required>
          <el-input v-model="createPolicyForm.owner" placeholder="Department or team name" />
        </el-form-item>
        <el-form-item label="Version">
          <el-input v-model="createPolicyForm.version" placeholder="1.0.0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createPolicyVisible = false">Cancel</el-button>
        <el-button type="primary" @click="createPolicy">Create Policy</el-button>
      </template>
    </el-dialog>

    <!-- Edit Policy Dialog -->
    <el-dialog v-model="editPolicyVisible" title="Edit Policy" width="550px">
      <el-form :model="editPolicyForm" label-width="120px">
        <el-form-item label="Policy Name" required>
          <el-input v-model="editPolicyForm.name" placeholder="Enter policy name" />
        </el-form-item>
        <el-form-item label="Category">
          <el-select v-model="editPolicyForm.category" style="width: 100%">
            <el-option v-for="c in categoryOptions.slice(1)" :key="c.value" :label="c.label" :value="c.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Status">
          <el-select v-model="editPolicyForm.status" style="width: 100%">
            <el-option label="Active" value="active" />
            <el-option label="Draft" value="draft" />
            <el-option label="Under Review" value="review" />
            <el-option label="Archived" value="archived" />
          </el-select>
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="editPolicyForm.description" type="textarea" rows="2" placeholder="Enter description" />
        </el-form-item>
        <el-form-item label="Owner" required>
          <el-input v-model="editPolicyForm.owner" placeholder="Department or team name" />
        </el-form-item>
        <el-form-item label="Version">
          <el-input v-model="editPolicyForm.version" placeholder="1.0.0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editPolicyVisible = false">Cancel</el-button>
        <el-button type="primary" @click="savePolicyEdit">Save Changes</el-button>
      </template>
    </el-dialog>
  </div>
</template>

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

/* ==================== Main Content ==================== */
.ai-policies-container {
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #eef2f6 100%);
  min-height: 100vh;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #1e293b 0%, #2d3a4e 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.header-right {
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
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.total-icon {
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
  color: #409eff;
}

.compliance-icon {
  background: linear-gradient(135deg, #f0f9ff 0%, #d4f1f9 100%);
  color: #67c23a;
}

.controls-icon {
  background: linear-gradient(135deg, #fdf6ec 0%, #f9e8cc 100%);
  color: #e6a23c;
}

.violations-icon {
  background: linear-gradient(135deg, #fef0f0 0%, #fcd9d9 100%);
  color: #f56c6c;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
  margin-top: 4px;
}

.stat-trend {
  position: absolute;
  top: 16px;
  right: 16px;
  font-size: 11px;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 20px;
}

.trend-up {
  color: #67c23a;
}

.trend-down {
  color: #f56c6c;
}

/* Chart Section */
.chart-section {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.compliance-chart {
  width: 100%;
}

/* Filters Bar */
.filters-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 24px;
}

.filters-left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.status-filters {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.status-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 40px;
  font-size: 13px;
  color: #606266;
  cursor: pointer;
  transition: all 0.2s ease;
}

.status-chip:hover {
  border-color: #409eff;
  color: #409eff;
}

.status-chip.active {
  background: #409eff;
  border-color: #409eff;
  color: white;
}

.chip-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.filters-right {
  display: flex;
  gap: 12px;
}

/* Policies Grid */
.policies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.policy-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  position: relative;
}

.policy-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

/* Card Header */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px 0 20px;
}

.policy-category {
  display: flex;
  align-items: center;
  gap: 8px;
}

.category-icon {
  font-size: 18px;
}

.category-name {
  font-size: 12px;
  font-weight: 600;
  color: #409eff;
  background: #e6f7ff;
  padding: 4px 8px;
  border-radius: 12px;
}

/* Card Body */
.card-body {
  padding: 16px 20px;
}

.policy-name {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 10px 0;
  line-height: 1.4;
}

.policy-description {
  font-size: 13px;
  color: #64748b;
  line-height: 1.5;
  margin: 0 0 16px 0;
}

.compliance-section {
  margin-bottom: 16px;
}

.compliance-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  font-size: 12px;
  color: #606266;
}

.compliance-value {
  font-weight: 600;
}

.compliance-bar {
  height: 6px;
  background: #e4e7ed;
  border-radius: 3px;
  overflow: hidden;
}

.compliance-bar .bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.key-metrics {
  display: flex;
  justify-content: space-around;
  margin-bottom: 16px;
  padding: 12px 0;
  border-top: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
}

.metric {
  text-align: center;
}

.metric-label {
  font-size: 11px;
  color: #909399;
  display: block;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.metric-value.has-violations {
  color: #f56c6c;
}

.dates {
  margin-bottom: 12px;
}

.date-item {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  margin-bottom: 4px;
}

.date-label {
  color: #909399;
}

.date-value {
  color: #1e293b;
  font-weight: 500;
}

.owner {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #909399;
}

/* Card Footer */
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px 16px 20px;
  border-top: 1px solid #f0f0f0;
  background: #fafbfc;
}

.last-reviewed {
  font-size: 11px;
  color: #909399;
}

.card-actions {
  display: flex;
  gap: 8px;
}

/* Empty State */
.empty-state {
  padding: 60px 0;
  text-align: center;
}

/* Pagination */
.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding-top: 8px;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .policies-grid {
    grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  }
}

@media (max-width: 768px) {
  .ai-policies-container {
    padding: 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .filters-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filters-left {
    flex-direction: column;
  }

  .status-filters {
    justify-content: center;
  }

  .page-header {
    flex-direction: column;
    text-align: center;
  }

  .header-right {
    width: 100%;
    justify-content: center;
  }

  .policies-grid {
    grid-template-columns: 1fr;
  }

  .card-footer {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }

  .key-metrics {
    flex-direction: column;
    gap: 8px;
  }
}
</style>