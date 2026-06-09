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
        <div class="loading-tip">Data Governance</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="data-governance-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Data Platform</el-breadcrumb-item>
            <el-breadcrumb-item>Data Governance</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Data Governance</h1>
        <p class="description">Manage data quality, compliance, privacy, and governance policies across the organization</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Report
        </el-button>
        <el-button type="primary" @click="handleCreatePolicy">
          <el-icon><Plus /></el-icon>
          Create Policy
        </el-button>
      </div>
    </div>

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

    <!-- Quality & Compliance Charts -->
    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :lg="14">
        <el-card class="quality-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Data Quality Score Trend</span>
              <el-select v-model="qualityDomain" size="small" style="width: 140px">
                <el-option label="All Domains" value="all" />
                <el-option label="Operations" value="Operations" />
                <el-option label="Finance" value="Finance" />
                <el-option label="Energy" value="Energy" />
                <el-option label="ESG" value="ESG" />
              </el-select>
            </div>
          </template>
          <div ref="qualityChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="10">
        <el-card class="compliance-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Compliance Status</span>
            </div>
          </template>
          <div ref="complianceChartRef" class="pie-chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Governance Tabs -->
    <el-card class="governance-tabs-card" shadow="hover">
      <el-tabs v-model="activeTab" @tab-click="handleTabChange">
        <el-tab-pane label="Data Quality" name="quality">
          <template #label>
            <span><el-icon><DataAnalysis /></el-icon> Data Quality</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="Data Compliance" name="compliance">
          <template #label>
            <span><el-icon><Document /></el-icon> Data Compliance</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="Data Privacy" name="privacy">
          <template #label>
            <span><el-icon><Lock /></el-icon> Data Privacy</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="Governance Policies" name="policies">
          <template #label>
            <span><el-icon><Setting /></el-icon> Governance Policies</span>
          </template>
        </el-tab-pane>
      </el-tabs>

      <!-- Data Quality Tab -->
      <div v-show="activeTab === 'quality'" class="tab-content">
        <div class="quality-metrics">
          <el-row :gutter="20">
            <el-col :span="6" v-for="metric in qualityMetrics" :key="metric.name">
              <div class="metric-card">
                <div class="metric-header">
                  <span class="metric-name">{{ metric.name }}</span>
                  <el-tag :type="metric.score >= 90 ? 'success' : metric.score >= 70 ? 'warning' : 'danger'" size="small">
                    {{ metric.score }}%
                  </el-tag>
                </div>
                <el-progress :percentage="metric.score" :color="metric.score >= 90 ? '#67c23a' : metric.score >= 70 ? '#e6a23c' : '#f56c6c'" />
                <div class="metric-footer">
                  <span>Target: {{ metric.target }}%</span>
                  <span class="trend" :class="metric.trend > 0 ? 'up' : 'down'">
                    {{ metric.trend > 0 ? '+' : '' }}{{ metric.trend }}%
                  </span>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>

        <div class="quality-issues">
          <h4>Open Data Quality Issues</h4>
          <el-table :data="qualityIssues" stripe size="small">
            <el-table-column prop="asset" label="Data Asset" width="200" />
            <el-table-column prop="issue" label="Issue Type" width="150" />
            <el-table-column prop="description" label="Description" min-width="250" />
            <el-table-column prop="severity" label="Severity" width="100">
              <template #default="{ row }">
                <el-tag :type="row.severity === 'High' ? 'danger' : row.severity === 'Medium' ? 'warning' : 'info'" size="small">
                  {{ row.severity }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="Status" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'Open' ? 'danger' : 'success'" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="Action" width="100">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="viewIssue(row)">View</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <!-- Data Compliance Tab -->
      <div v-show="activeTab === 'compliance'" class="tab-content">
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="compliance-regulations">
              <h4>Regulatory Compliance</h4>
              <div v-for="reg in regulations" :key="reg.name" class="regulation-item">
                <div class="regulation-header">
                  <span class="regulation-name">{{ reg.name }}</span>
                  <el-tag :type="reg.status === 'Compliant' ? 'success' : 'warning'" size="small">{{ reg.status }}</el-tag>
                </div>
                <el-progress :percentage="reg.progress" :color="reg.status === 'Compliant' ? '#67c23a' : '#e6a23c'" />
                <div class="regulation-details">
                  <span>Last Audit: {{ reg.lastAudit }}</span>
                  <span>Next Audit: {{ reg.nextAudit }}</span>
                </div>
              </div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="compliance-audits">
              <h4>Recent Audit Results</h4>
              <el-table :data="auditResults" stripe size="small">
                <el-table-column prop="date" label="Date" width="100" />
                <el-table-column prop="regulation" label="Regulation" width="120" />
                <el-table-column prop="score" label="Score" width="80">
                  <template #default="{ row }">
                    <span :style="{ color: row.score >= 85 ? '#67c23a' : row.score >= 70 ? '#e6a23c' : '#f56c6c' }">
                      {{ row.score }}%
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="findings" label="Findings" width="80" align="center" />
                <el-table-column prop="status" label="Status" width="100">
                  <template #default="{ row }">
                    <el-tag :type="row.status === 'Passed' ? 'success' : 'danger'" size="small">{{ row.status }}</el-tag>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- Data Privacy Tab -->
      <div v-show="activeTab === 'privacy'" class="tab-content">
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="privacy-classification">
              <h4>Data Classification</h4>
              <div ref="classificationChartRef" class="classification-chart"></div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="privacy-requests">
              <h4>Data Subject Requests</h4>
              <el-table :data="privacyRequests" stripe size="small">
                <el-table-column prop="id" label="ID" width="80" />
                <el-table-column prop="type" label="Type" width="120">
                  <template #default="{ row }">
                    <el-tag size="small">{{ row.type }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="requester" label="Requester" width="130" />
                <el-table-column prop="submitted" label="Submitted" width="100" />
                <el-table-column prop="status" label="Status" width="100">
                  <template #default="{ row }">
                    <el-tag :type="row.status === 'Completed' ? 'success' : 'warning'" size="small">{{ row.status }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="Action" width="80">
                  <template #default="{ row }">
                    <el-button link type="primary" size="small" @click="viewRequest(row)">View</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- Governance Policies Tab -->
      <div v-show="activeTab === 'policies'" class="tab-content">
        <div class="policies-header">
          <el-input
              v-model="policySearch"
              placeholder="Search policies..."
              prefix-icon="Search"
              clearable
              style="width: 300px"
          />
        </div>
        <el-table :data="filteredPolicies" stripe>
          <el-table-column prop="name" label="Policy Name" min-width="200" />
          <el-table-column prop="category" label="Category" width="150">
            <template #default="{ row }">
              <el-tag :type="getPolicyCategoryTag(row.category)" size="small">{{ row.category }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="version" label="Version" width="80" />
          <el-table-column prop="owner" label="Owner" width="130" />
          <el-table-column prop="effectiveDate" label="Effective Date" width="110" />
          <el-table-column prop="status" label="Status" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'Active' ? 'success' : 'info'" size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="Actions" width="150">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="viewPolicy(row)">View</el-button>
              <el-button link type="success" size="small" @click="editPolicy(row)">Edit</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- Create/Edit Policy Dialog -->
    <el-dialog v-model="policyDialogVisible" :title="dialogMode === 'create' ? 'Create Governance Policy' : 'Edit Policy'" width="600px" destroy-on-close>
      <el-form :model="policyForm" :rules="policyRules" ref="policyFormRef" label-width="120px">
        <el-form-item label="Policy Name" prop="name">
          <el-input v-model="policyForm.name" placeholder="Enter policy name" />
        </el-form-item>
        <el-form-item label="Category" prop="category">
          <el-select v-model="policyForm.category" placeholder="Select category" style="width: 100%">
            <el-option label="Data Quality" value="Data Quality" />
            <el-option label="Data Retention" value="Data Retention" />
            <el-option label="Data Privacy" value="Data Privacy" />
            <el-option label="Data Security" value="Data Security" />
            <el-option label="Compliance" value="Compliance" />
          </el-select>
        </el-form-item>
        <el-form-item label="Owner" prop="owner">
          <el-input v-model="policyForm.owner" placeholder="Enter owner name" />
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="policyForm.description" type="textarea" :rows="3" placeholder="Enter policy description" />
        </el-form-item>
        <el-form-item label="Effective Date" prop="effectiveDate">
          <el-date-picker v-model="policyForm.effectiveDate" type="date" placeholder="Select date" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Status" prop="status">
          <el-select v-model="policyForm.status" placeholder="Select status" style="width: 100%">
            <el-option label="Active" value="Active" />
            <el-option label="Draft" value="Draft" />
            <el-option label="Archived" value="Archived" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="policyDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitPolicy">Save Policy</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Plus, ArrowUp, ArrowDown, Document, Checked,
  Clock, TrendCharts, Refresh, Search, Download, Setting,
  DataAnalysis, Lock, Filter, User
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading governance data...',
  'Checking compliance status...',
  'Almost ready...'
]

// ==================== Chart References ====================
const qualityChartRef = ref<HTMLElement>()
const complianceChartRef = ref<HTMLElement>()
const classificationChartRef = ref<HTMLElement>()
let qualityChart: echarts.ECharts | null = null
let complianceChart: echarts.ECharts | null = null
let classificationChart: echarts.ECharts | null = null

// ==================== State ====================
const activeTab = ref('quality')
const qualityDomain = ref('all')
const policySearch = ref('')
const policyDialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const policyFormRef = ref()

const statsCards = ref([
  { title: 'Data Quality Score', value: '86%', trend: 5, icon: 'DataAnalysis', bgColor: '#409eff', key: 'quality' },
  { title: 'Compliance Rate', value: '94%', trend: 3, icon: 'Checked', bgColor: '#67c23a', key: 'compliance' },
  { title: 'Active Policies', value: 24, trend: 8, icon: 'Document', bgColor: '#e6a23c', key: 'policies' },
  { title: 'Open Issues', value: 12, trend: -15, icon: 'TrendCharts', bgColor: '#f56c6c', key: 'issues' }
])

const qualityMetrics = ref([
  { name: 'Completeness', score: 92, target: 95, trend: 2 },
  { name: 'Accuracy', score: 88, target: 90, trend: 3 },
  { name: 'Consistency', score: 85, target: 88, trend: -1 },
  { name: 'Timeliness', score: 79, target: 85, trend: 4 }
])

const qualityIssues = ref([
  { id: 1, asset: 'device_master', issue: 'Missing Values', description: '15% of records missing location field', severity: 'Medium', status: 'Open' },
  { id: 2, asset: 'energy_consumption', issue: 'Outliers', description: 'Unusual consumption spikes detected on weekends', severity: 'High', status: 'In Progress' },
  { id: 3, asset: 'customer_contract', issue: 'Duplicate Records', description: 'Duplicate contract records found', severity: 'High', status: 'Open' },
  { id: 4, asset: 'esg_carbon_footprint', issue: 'Data Stale', description: 'Some records not updated for 30+ days', severity: 'Low', status: 'Resolved' }
])

const regulations = ref([
  { name: 'GDPR', status: 'Compliant', progress: 100, lastAudit: '2024-01-10', nextAudit: '2024-04-10' },
  { name: 'CCPA', status: 'Compliant', progress: 100, lastAudit: '2024-01-05', nextAudit: '2024-04-05' },
  { name: 'SOX', status: 'In Progress', progress: 85, lastAudit: '2024-01-15', nextAudit: '2024-04-15' },
  { name: 'ISO 27001', status: 'Compliant', progress: 100, lastAudit: '2024-01-08', nextAudit: '2024-04-08' }
])

const auditResults = ref([
  { date: '2024-01-10', regulation: 'GDPR', score: 98, findings: 1, status: 'Passed' },
  { date: '2024-01-05', regulation: 'CCPA', score: 95, findings: 2, status: 'Passed' },
  { date: '2024-01-15', regulation: 'SOX', score: 82, findings: 4, status: 'Warning' },
  { date: '2024-01-08', regulation: 'ISO 27001', score: 96, findings: 1, status: 'Passed' }
])

const privacyRequests = ref([
  { id: 'R001', type: 'Access Request', requester: 'John Doe', submitted: '2024-01-18', status: 'Completed' },
  { id: 'R002', type: 'Deletion Request', requester: 'Jane Smith', submitted: '2024-01-15', status: 'In Progress' },
  { id: 'R003', type: 'Rectification', requester: 'Bob Johnson', submitted: '2024-01-10', status: 'Completed' },
  { id: 'R004', type: 'Access Request', requester: 'Alice Brown', submitted: '2024-01-05', status: 'Completed' }
])

const governancePolicies = ref([
  { id: 1, name: 'Data Quality Management Policy', category: 'Data Quality', version: '2.1', owner: 'John Smith', effectiveDate: '2024-01-01', status: 'Active' },
  { id: 2, name: 'Data Retention and Archival', category: 'Data Retention', version: '1.5', owner: 'Sarah Chen', effectiveDate: '2024-01-01', status: 'Active' },
  { id: 3, name: 'Personal Data Protection', category: 'Data Privacy', version: '3.0', owner: 'Emily Zhao', effectiveDate: '2024-01-15', status: 'Active' },
  { id: 4, name: 'Data Access Control', category: 'Data Security', version: '2.0', owner: 'Tom Harris', effectiveDate: '2024-01-01', status: 'Active' },
  { id: 5, name: 'GDPR Compliance Framework', category: 'Compliance', version: '1.2', owner: 'Maria Garcia', effectiveDate: '2024-01-10', status: 'Draft' },
  { id: 6, name: 'Data Classification Standard', category: 'Data Privacy', version: '1.0', owner: 'Emily Zhao', effectiveDate: '2024-02-01', status: 'Draft' }
])

const policyForm = reactive({
  name: '',
  category: '',
  owner: '',
  description: '',
  effectiveDate: '',
  status: 'Draft'
})

const policyRules = {
  name: [{ required: true, message: 'Please enter policy name', trigger: 'blur' }],
  category: [{ required: true, message: 'Please select category', trigger: 'change' }],
  owner: [{ required: true, message: 'Please enter owner', trigger: 'blur' }],
  effectiveDate: [{ required: true, message: 'Please select effective date', trigger: 'change' }]
}

// ==================== Computed ====================
const filteredPolicies = computed(() => {
  if (!policySearch.value) return governancePolicies.value
  return governancePolicies.value.filter(p =>
      p.name.toLowerCase().includes(policySearch.value.toLowerCase())
  )
})

// ==================== Helper Methods ====================
const getPolicyCategoryTag = (category: string) => {
  const map: Record<string, string> = {
    'Data Quality': 'primary',
    'Data Retention': 'warning',
    'Data Privacy': 'success',
    'Data Security': 'danger',
    'Compliance': 'info'
  }
  return map[category] || 'info'
}

// ==================== Chart Initializations ====================
const initQualityChart = () => {
  if (!qualityChartRef.value) return
  if (qualityChart) qualityChart.dispose()

  qualityChart = echarts.init(qualityChartRef.value)

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['Completeness', 'Accuracy', 'Consistency', 'Timeliness'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '12%', containLabel: true },
    xAxis: { type: 'category', data: ['Week 1', 'Week 2', 'Week 3', 'Week 4'] },
    yAxis: { type: 'value', name: 'Score (%)', min: 60, max: 100 },
    series: [
      { name: 'Completeness', type: 'line', data: [88, 89, 91, 92], smooth: true, lineStyle: { width: 2 } },
      { name: 'Accuracy', type: 'line', data: [84, 85, 87, 88], smooth: true, lineStyle: { width: 2 } },
      { name: 'Consistency', type: 'line', data: [82, 83, 84, 85], smooth: true, lineStyle: { width: 2 } },
      { name: 'Timeliness', type: 'line', data: [72, 75, 77, 79], smooth: true, lineStyle: { width: 2 } }
    ]
  }

  qualityChart.setOption(option)
  window.addEventListener('resize', () => qualityChart?.resize())
}

const initComplianceChart = () => {
  if (!complianceChartRef.value) return
  if (complianceChart) complianceChart.dispose()

  complianceChart = echarts.init(complianceChartRef.value)

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'item', formatter: '{b}: {d}%' },
    series: [{
      type: 'pie',
      radius: '55%',
      data: [
        { value: 75, name: 'Compliant', itemStyle: { color: '#67c23a' } },
        { value: 15, name: 'Partial', itemStyle: { color: '#e6a23c' } },
        { value: 10, name: 'Non-Compliant', itemStyle: { color: '#f56c6c' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  }

  complianceChart.setOption(option)
  window.addEventListener('resize', () => complianceChart?.resize())
}

const initClassificationChart = () => {
  if (!classificationChartRef.value) return
  if (classificationChart) classificationChart.dispose()

  classificationChart = echarts.init(classificationChartRef.value)

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'item', formatter: '{b}: {d}%' },
    series: [{
      type: 'pie',
      radius: '55%',
      data: [
        { value: 45, name: 'Public', itemStyle: { color: '#67c23a' } },
        { value: 30, name: 'Internal', itemStyle: { color: '#409eff' } },
        { value: 15, name: 'Confidential', itemStyle: { color: '#e6a23c' } },
        { value: 10, name: 'Restricted', itemStyle: { color: '#f56c6c' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  }

  classificationChart.setOption(option)
  window.addEventListener('resize', () => classificationChart?.resize())
}

// ==================== Interactive Methods ====================
const handleCardClick = (stat: any) => {
  ElMessage.info(`Viewing ${stat.title} details`)
}

const handleExport = () => {
  ElMessage.success('Exporting governance report...')
}

const handleCreatePolicy = () => {
  dialogMode.value = 'create'
  Object.assign(policyForm, {
    name: '',
    category: '',
    owner: '',
    description: '',
    effectiveDate: '',
    status: 'Draft'
  })
  policyDialogVisible.value = true
}

const handleTabChange = () => {
  if (activeTab.value === 'privacy') {
    nextTick(() => initClassificationChart())
  }
}

const viewIssue = (issue: any) => {
  ElMessage.info(`Viewing issue: ${issue.asset} - ${issue.issue}`)
}

const viewRequest = (request: any) => {
  ElMessage.info(`Viewing request: ${request.id} - ${request.type}`)
}

const viewPolicy = (policy: any) => {
  ElMessage.info(`Viewing policy: ${policy.name}`)
}

const editPolicy = (policy: any) => {
  dialogMode.value = 'edit'
  Object.assign(policyForm, policy)
  policyDialogVisible.value = true
}

const submitPolicy = async () => {
  if (!policyFormRef.value) return
  await policyFormRef.value.validate((valid: boolean) => {
    if (valid) {
      ElMessage.success(`Policy "${policyForm.name}" saved successfully`)
      policyDialogVisible.value = false
      policyFormRef.value?.resetFields()
    }
  })
}

// ==================== Loading Simulation ====================
const initCharts = async () => {
  await nextTick()
  setTimeout(() => {
    initQualityChart()
    initComplianceChart()
    initClassificationChart()
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
.data-governance-page {
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

.chart-row {
  margin-bottom: 20px;
}

.quality-card, .compliance-card {
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

.pie-chart-container {
  width: 100%;
  height: 300px;
}

.governance-tabs-card {
  .tab-content {
    padding: 20px 0;
  }
}

.quality-metrics {
  margin-bottom: 24px;

  .metric-card {
    background: #f5f7fa;
    border-radius: 8px;
    padding: 16px;

    .metric-header {
      display: flex;
      justify-content: space-between;
      margin-bottom: 12px;

      .metric-name {
        font-weight: 600;
        color: #303133;
      }
    }

    .metric-footer {
      display: flex;
      justify-content: space-between;
      margin-top: 8px;
      font-size: 12px;
      color: #909399;

      .trend {
        &.up { color: #67c23a; }
        &.down { color: #f56c6c; }
      }
    }
  }
}

.quality-issues {
  h4 {
    margin-bottom: 12px;
    color: #303133;
  }
}

.compliance-regulations, .compliance-audits {
  h4 {
    margin-bottom: 12px;
    color: #303133;
  }
}

.regulation-item {
  margin-bottom: 20px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;

  .regulation-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;

    .regulation-name {
      font-weight: 600;
      color: #303133;
    }
  }

  .regulation-details {
    display: flex;
    justify-content: space-between;
    margin-top: 8px;
    font-size: 12px;
    color: #909399;
  }
}

.privacy-classification {
  .classification-chart {
    width: 100%;
    height: 300px;
  }
}

.privacy-requests {
  h4 {
    margin-bottom: 12px;
    color: #303133;
  }
}

.policies-header {
  margin-bottom: 16px;
}

:deep(.el-table) {
  font-size: 13px;
}

:deep(.el-tabs__header) {
  margin-bottom: 0;
}
</style>