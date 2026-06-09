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
        <div class="loading-tip">Approval Steps Configuration</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="approval-steps-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Decision & Evidence</el-breadcrumb-item>
            <el-breadcrumb-item>Workflow Management</el-breadcrumb-item>
            <el-breadcrumb-item>Approval Steps</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Approval Steps</h1>
        <p class="description">Configure and manage sequential approval steps, routing rules, and step-specific requirements</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export
        </el-button>
        <el-button type="primary" @click="handleCreateStep">
          <el-icon><Plus /></el-icon>
          New Approval Step
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

    <!-- Rule Selector -->
    <el-card class="rule-selector-card" shadow="hover">
      <div class="rule-selector-container">
        <div class="selector-label">Select Approval Rule:</div>
        <el-select v-model="selectedRuleId" placeholder="Choose an approval rule" filterable style="width: 400px" @change="handleRuleChange">
          <el-option
              v-for="rule in approvalRules"
              :key="rule.id"
              :label="`${rule.ruleName} (${rule.decisionType} - ${rule.priority})`"
              :value="rule.id"
          />
        </el-select>
        <el-tag v-if="selectedRule" :type="getStatusTag(selectedRule.status)" size="default" style="margin-left: 16px">
          {{ selectedRule.status }}
        </el-tag>
      </div>
    </el-card>

    <!-- Steps Flow Diagram -->
    <el-card class="flow-diagram-card" shadow="hover" v-if="selectedRule">
      <template #header>
        <div class="card-header">
          <span>Approval Flow Diagram</span>
          <el-button size="small" @click="handleRefreshFlow">
            <el-icon><Refresh /></el-icon>
            Refresh
          </el-button>
        </div>
      </template>
      <div ref="flowChartRef" class="flow-chart-container"></div>
    </el-card>

    <!-- Steps List -->
    <el-card class="steps-card" shadow="hover" v-if="selectedRule">
      <template #header>
        <div class="card-header">
          <span>Approval Steps Configuration</span>
          <div class="table-actions">
            <el-button :icon="Refresh" @click="fetchSteps" circle />
            <el-button type="primary" size="small" @click="handleAddStep">
              <el-icon><Plus /></el-icon>
              Add Step
            </el-button>
          </div>
        </div>
      </template>

      <div class="steps-timeline">
        <div v-for="(step, index) in stepsList" :key="step.id" class="step-item" :class="{ 'completed': step.status === 'active' }">
          <div class="step-marker">
            <div class="step-number">{{ index + 1 }}</div>
            <div v-if="index < stepsList.length - 1" class="step-line"></div>
          </div>
          <div class="step-card">
            <div class="step-header">
              <div class="step-title">
                <span class="step-name">{{ step.stepName }}</span>
                <el-tag :type="getStepTypeTag(step.stepType)" size="small">{{ step.stepType }}</el-tag>
                <el-tag :type="getStatusTag(step.status)" size="small">{{ step.status }}</el-tag>
              </div>
              <div class="step-actions">
                <el-button link type="primary" size="small" @click="viewStep(step)">View</el-button>
                <el-button link type="success" size="small" @click="editStep(step)">Edit</el-button>
                <el-button link type="danger" size="small" @click="deleteStep(step)">Delete</el-button>
                <el-button v-if="step.order > 1" link type="info" size="small" @click="moveStepUp(step)">↑ Up</el-button>
                <el-button v-if="step.order < stepsList.length" link type="info" size="small" @click="moveStepDown(step)">↓ Down</el-button>
              </div>
            </div>
            <div class="step-content">
              <el-row :gutter="16">
                <el-col :span="8">
                  <div class="step-info">
                    <span class="info-label">Approvers:</span>
                    <span class="info-value">{{ getApproverNames(step.approvers) }}</span>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="step-info">
                    <span class="info-label">Min Approvers:</span>
                    <span class="info-value">{{ step.minApprovers }}</span>
                  </div>
                </el-col>
                <el-col :span="5">
                  <div class="step-info">
                    <span class="info-label">Timeout:</span>
                    <span class="info-value">{{ step.timeoutHours }} hours</span>
                  </div>
                </el-col>
                <el-col :span="5">
                  <div class="step-info">
                    <span class="info-label">Action:</span>
                    <span class="info-value">{{ step.escalationAction || 'N/A' }}</span>
                  </div>
                </el-col>
              </el-row>
              <div class="step-description" v-if="step.description">
                <span class="info-label">Description:</span>
                <span class="info-value">{{ step.description }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- Step Detail Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogMode === 'create' ? 'Create Approval Step' : (dialogMode === 'edit' ? 'Edit Approval Step' : 'Approval Step Details')" width="700px" destroy-on-close>
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="140px" :disabled="dialogMode === 'view'">
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="Step Name" prop="stepName">
              <el-input v-model="formData.stepName" placeholder="Enter step name (e.g., Technical Review, Manager Approval)" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Step Type" prop="stepType">
              <el-select v-model="formData.stepType" placeholder="Select step type" style="width: 100%">
                <el-option label="Technical Review" value="Technical Review" />
                <el-option label="Financial Review" value="Financial Review" />
                <el-option label="Legal Review" value="Legal Review" />
                <el-option label="Management Approval" value="Management Approval" />
                <el-option label="Executive Approval" value="Executive Approval" />
                <el-option label="ESG Review" value="ESG Review" />
                <el-option label="Safety Review" value="Safety Review" />
                <el-option label="IT Review" value="IT Review" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Status" prop="status">
              <el-select v-model="formData.status" placeholder="Select status" style="width: 100%">
                <el-option label="Active" value="Active" />
                <el-option label="Inactive" value="Inactive" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Minimum Approvers" prop="minApprovers">
              <el-input-number v-model="formData.minApprovers" :min="1" :max="10" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Timeout (hours)" prop="timeoutHours">
              <el-input-number v-model="formData.timeoutHours" :min="0" :max="168" :step="1" style="width: 100%" />
              <span style="margin-left: 8px; color: #909399">0 = no timeout</span>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="Approvers" prop="approvers">
              <el-select v-model="formData.approvers" multiple filterable placeholder="Select approvers for this step" style="width: 100%">
                <el-option
                    v-for="approver in availableApprovers"
                    :key="approver.id"
                    :label="`${approver.name} (${approver.role}) - ${approver.department}`"
                    :value="approver.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Escalation Action" prop="escalationAction">
              <el-select v-model="formData.escalationAction" placeholder="Select escalation action" clearable style="width: 100%">
                <el-option label="Notify Manager" value="Notify Manager" />
                <el-option label="Auto-approve" value="Auto-approve" />
                <el-option label="Reject" value="Reject" />
                <el-option label="Escalate to Next Level" value="Escalate to Next Level" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Conditional Rule" prop="conditionalRule">
              <el-select v-model="formData.conditionalRule" placeholder="Select conditional rule" clearable style="width: 100%">
                <el-option label="Always Required" value="Always Required" />
                <el-option label="If Amount > $10k" value="If Amount > $10k" />
                <el-option label="If Amount > $50k" value="If Amount > $50k" />
                <el-option label="If Priority = Critical" value="If Priority = Critical" />
                <el-option label="If High Risk" value="If High Risk" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="Description" prop="description">
              <el-input v-model="formData.description" type="textarea" :rows="2" placeholder="Enter step description and requirements" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Close</el-button>
        <el-button v-if="dialogMode !== 'view'" type="primary" @click="submitForm">Save Step</el-button>
      </template>
    </el-dialog>

    <!-- Delete Confirmation Dialog -->
    <el-dialog v-model="deleteDialogVisible" title="Confirm Delete" width="400px">
      <p>Are you sure you want to delete approval step "{{ deleteTarget?.stepName }}"?</p>
      <p style="color: #f56c6c; font-size: 12px; margin-top: 8px">This action cannot be undone.</p>
      <template #footer>
        <el-button @click="deleteDialogVisible = false">Cancel</el-button>
        <el-button type="danger" @click="confirmDelete">Delete</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  Plus, ArrowUp, ArrowDown, Document, Checked,
  Clock, TrendCharts, Refresh, Search, Download, Setting, Delete
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading approval steps...',
  'Configuring workflows...',
  'Almost ready...'
]

// ==================== Interfaces ====================
interface Approver {
  id: number
  name: string
  role: string
  email: string
  department: string
}

interface ApprovalStep {
  id: number
  stepName: string
  stepType: string
  order: number
  approvers: number[]
  minApprovers: number
  timeoutHours: number
  escalationAction: string
  conditionalRule: string
  status: string
  description: string
  createdAt: string
  updatedAt: string
}

interface ApprovalRule {
  id: number
  ruleName: string
  decisionType: string
  priority: string
  status: string
  steps: ApprovalStep[]
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
const flowChartRef = ref<HTMLElement>()
let flowChart: echarts.ECharts | null = null

// ==================== Mock Data ====================
const statsCards = ref<StatCard[]>([
  { title: 'Total Steps', value: 28, trend: 6, icon: 'Document', bgColor: '#409eff', key: 'total' },
  { title: 'Active Steps', value: 22, trend: 4, icon: 'Checked', bgColor: '#67c23a', key: 'active' },
  { title: 'Avg Steps per Rule', value: '3.5', trend: 2, icon: 'TrendCharts', bgColor: '#e6a23c', key: 'avg' },
  { title: 'Avg Timeout (hrs)', value: '48', trend: -8, icon: 'Clock', bgColor: '#f56c6c', key: 'timeout' }
])

const availableApprovers = ref<Approver[]>([
  { id: 1, name: 'John Smith', role: 'Facility Manager', email: 'john.smith@ibms.com', department: 'Facilities' },
  { id: 2, name: 'Sarah Chen', role: 'Operations Director', email: 'sarah.chen@ibms.com', department: 'Operations' },
  { id: 3, name: 'David Wang', role: 'Chief Engineer', email: 'david.wang@ibms.com', department: 'Engineering' },
  { id: 4, name: 'Lisa Zhang', role: 'Energy Manager', email: 'lisa.zhang@ibms.com', department: 'Energy' },
  { id: 5, name: 'Mike Johnson', role: 'Maintenance Supervisor', email: 'mike.johnson@ibms.com', department: 'Maintenance' },
  { id: 6, name: 'Emily Zhao', role: 'ESG Manager', email: 'emily.zhao@ibms.com', department: 'ESG' },
  { id: 7, name: 'Robert Liu', role: 'Safety Officer', email: 'robert.liu@ibms.com', department: 'Safety' },
  { id: 8, name: 'Tom Harris', role: 'IT Director', email: 'tom.harris@ibms.com', department: 'IT' },
  { id: 9, name: 'Anna Kim', role: 'Finance Controller', email: 'anna.kim@ibms.com', department: 'Finance' },
  { id: 10, name: 'James Wu', role: 'VP of Operations', email: 'james.wu@ibms.com', department: 'Executive' },
  { id: 11, name: 'Maria Garcia', role: 'Legal Counsel', email: 'maria.garcia@ibms.com', department: 'Legal' },
  { id: 12, name: 'Chris Lee', role: 'Procurement Manager', email: 'chris.lee@ibms.com', department: 'Procurement' }
])

const approvalRules = ref<ApprovalRule[]>([
  {
    id: 1,
    ruleName: 'Critical Fault Resolution',
    decisionType: 'Fault Decision',
    priority: 'Critical',
    status: 'Active',
    steps: [
      {
        id: 101,
        stepName: 'Technical Assessment',
        stepType: 'Technical Review',
        order: 1,
        approvers: [3, 5, 8],
        minApprovers: 1,
        timeoutHours: 24,
        escalationAction: 'Notify Manager',
        conditionalRule: 'Always Required',
        status: 'Active',
        description: 'Technical team reviews the fault and recommends solution',
        createdAt: '2024-01-01',
        updatedAt: '2024-01-15'
      },
      {
        id: 102,
        stepName: 'Management Approval',
        stepType: 'Management Approval',
        order: 2,
        approvers: [1, 2],
        minApprovers: 1,
        timeoutHours: 48,
        escalationAction: 'Escalate to Next Level',
        conditionalRule: 'Always Required',
        status: 'Active',
        description: 'Management reviews technical recommendation and approves budget',
        createdAt: '2024-01-01',
        updatedAt: '2024-01-15'
      },
      {
        id: 103,
        stepName: 'Executive Sign-off',
        stepType: 'Executive Approval',
        order: 3,
        approvers: [10],
        minApprovers: 1,
        timeoutHours: 72,
        escalationAction: 'Auto-approve',
        conditionalRule: 'If Amount > $50k',
        status: 'Active',
        description: 'Final executive approval for high-value decisions',
        createdAt: '2024-01-01',
        updatedAt: '2024-01-15'
      }
    ]
  },
  {
    id: 2,
    ruleName: 'Major Maintenance Decision',
    decisionType: 'Maintenance Decision',
    priority: 'High',
    status: 'Active',
    steps: [
      {
        id: 201,
        stepName: 'Technical Assessment',
        stepType: 'Technical Review',
        order: 1,
        approvers: [5, 3],
        minApprovers: 1,
        timeoutHours: 24,
        escalationAction: 'Notify Manager',
        conditionalRule: 'Always Required',
        status: 'Active',
        description: 'Maintenance team assesses the issue and provides solution',
        createdAt: '2024-01-02',
        updatedAt: '2024-01-10'
      },
      {
        id: 202,
        stepName: 'Manager Approval',
        stepType: 'Management Approval',
        order: 2,
        approvers: [1],
        minApprovers: 1,
        timeoutHours: 48,
        escalationAction: 'Escalate to Next Level',
        conditionalRule: 'Always Required',
        status: 'Active',
        description: 'Facility manager approves the maintenance plan',
        createdAt: '2024-01-02',
        updatedAt: '2024-01-10'
      },
      {
        id: 203,
        stepName: 'Ops Director Review',
        stepType: 'Management Approval',
        order: 3,
        approvers: [2],
        minApprovers: 1,
        timeoutHours: 48,
        escalationAction: 'Escalate to Next Level',
        conditionalRule: 'If Amount > $25k',
        status: 'Active',
        description: 'Operations director reviews major maintenance decisions',
        createdAt: '2024-01-02',
        updatedAt: '2024-01-10'
      }
    ]
  },
  {
    id: 3,
    ruleName: 'ESG Initiative Approval',
    decisionType: 'ESG Decision',
    priority: 'High',
    status: 'Active',
    steps: [
      {
        id: 301,
        stepName: 'ESG Review',
        stepType: 'ESG Review',
        order: 1,
        approvers: [6],
        minApprovers: 1,
        timeoutHours: 48,
        escalationAction: 'Notify Manager',
        conditionalRule: 'Always Required',
        status: 'Active',
        description: 'ESG team evaluates environmental and social impact',
        createdAt: '2024-01-03',
        updatedAt: '2024-01-12'
      },
      {
        id: 302,
        stepName: 'Sustainability Committee',
        stepType: 'Management Approval',
        order: 2,
        approvers: [2, 4, 6],
        minApprovers: 2,
        timeoutHours: 72,
        escalationAction: 'Escalate to Next Level',
        conditionalRule: 'Always Required',
        status: 'Active',
        description: 'Committee reviews ESG initiative and recommends approval',
        createdAt: '2024-01-03',
        updatedAt: '2024-01-12'
      },
      {
        id: 303,
        stepName: 'Executive Approval',
        stepType: 'Executive Approval',
        order: 3,
        approvers: [10, 2],
        minApprovers: 1,
        timeoutHours: 96,
        escalationAction: 'Auto-approve',
        conditionalRule: 'If Amount > $100k',
        status: 'Active',
        description: 'Executive team final approval',
        createdAt: '2024-01-03',
        updatedAt: '2024-01-12'
      }
    ]
  }
])

// ==================== Reactive Variables ====================
const selectedRuleId = ref<number>(1)
const selectedRule = computed(() => approvalRules.value.find(r => r.id === selectedRuleId.value))
const stepsList = computed(() => selectedRule.value?.steps || [])
const tableLoading = ref(false)
const dialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit' | 'view'>('view')
const deleteTarget = ref<ApprovalStep | null>(null)
const formRef = ref()

const formData = reactive<ApprovalStep>({
  id: 0,
  stepName: '',
  stepType: '',
  order: 1,
  approvers: [],
  minApprovers: 1,
  timeoutHours: 24,
  escalationAction: '',
  conditionalRule: 'Always Required',
  status: 'Active',
  description: '',
  createdAt: '',
  updatedAt: ''
})

const formRules = {
  stepName: [{ required: true, message: 'Please enter step name', trigger: 'blur' }],
  stepType: [{ required: true, message: 'Please select step type', trigger: 'change' }],
  approvers: [{ required: true, message: 'Please select at least one approver', trigger: 'change' }],
  minApprovers: [{ required: true, message: 'Please set minimum approvers', trigger: 'blur' }]
}

// ==================== Helper Methods ====================
const getStatusTag = (status: string): string => {
  const map: Record<string, string> = {
    'Active': 'success',
    'Inactive': 'info',
    'Draft': 'warning'
  }
  return map[status] || 'info'
}

const getStepTypeTag = (stepType: string): string => {
  const map: Record<string, string> = {
    'Technical Review': 'primary',
    'Financial Review': 'warning',
    'Legal Review': 'danger',
    'Management Approval': 'success',
    'Executive Approval': 'danger',
    'ESG Review': 'success',
    'Safety Review': 'warning',
    'IT Review': 'info'
  }
  return map[stepType] || 'info'
}

const getApproverNames = (approverIds: number[]): string => {
  if (!approverIds || approverIds.length === 0) return 'No approvers assigned'
  return approverIds.map(id => {
    const approver = availableApprovers.value.find(a => a.id === id)
    return approver ? `${approver.name} (${approver.role})` : ''
  }).join(', ')
}

// ==================== Chart Initialization ====================
const initFlowChart = () => {
  if (!flowChartRef.value || !selectedRule.value) return
  if (flowChart) flowChart.dispose()

  flowChart = echarts.init(flowChartRef.value)

  const steps = selectedRule.value.steps.sort((a, b) => a.order - b.order)
  const nodes = steps.map((step, index) => ({
    name: step.stepName,
    category: index,
    symbolSize: 50,
    itemStyle: { color: step.status === 'Active' ? '#67c23a' : '#909399' }
  }))

  const links = []
  for (let i = 0; i < steps.length - 1; i++) {
    links.push({ source: i, target: i + 1 })
  }

  const categories = steps.map((step, index) => ({ name: `Step ${index + 1}` }))

  const option: echarts.EChartsOption = {
    title: {
      text: `${selectedRule.value.ruleName} - Approval Flow`,
      left: 'center',
      top: 0
    },
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        if (params.dataType === 'node') {
          const step = steps[params.dataIndex]
          return `<strong>${step.stepName}</strong><br/>
                  Type: ${step.stepType}<br/>
                  Approvers: ${getApproverNames(step.approvers)}<br/>
                  Timeout: ${step.timeoutHours} hours`
        }
        return params.dataType
      }
    },
    series: [{
      type: 'graph',
      layout: 'force',
      force: {
        repulsion: 500,
        edgeLength: 150,
        gravity: 0.1,
        friction: 0.1
      },
      data: nodes,
      links: links,
      categories: categories,
      roam: true,
      draggable: true,
      focusNodeAdjacency: false,
      edgeSymbol: ['none', 'arrow'],
      edgeSymbolSize: [0, 10],
      edgeLabel: {
        show: true,
        formatter: '→',
        position: 'middle'
      },
      lineStyle: {
        color: '#409eff',
        width: 2,
        curveness: 0.3
      },
      label: {
        show: true,
        position: 'bottom',
        formatter: (params: any) => {
          return params.name
        },
        fontSize: 12
      },
      emphasis: {
        scale: true,
        label: {
          show: true
        }
      }
    }]
  }

  flowChart.setOption(option)
  window.addEventListener('resize', () => flowChart?.resize())
}

// ==================== Interactive Methods ====================
const handleCardClick = (stat: StatCard) => {
  ElMessage.info(`Viewing ${stat.title} details`)
}

const handleRuleChange = () => {
  initFlowChart()
  fetchSteps()
}

const handleRefreshFlow = () => {
  initFlowChart()
  ElMessage.success('Flow diagram refreshed')
}

const handleExport = () => {
  ElMessage.success(`Exporting approval steps configuration...`)
}

const fetchSteps = () => {
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
    ElMessage.success('Steps refreshed')
  }, 500)
}

const handleCreateStep = () => {
  if (!selectedRule.value) {
    ElMessage.warning('Please select an approval rule first')
    return
  }
  dialogMode.value = 'create'
  Object.assign(formData, {
    id: Date.now(),
    stepName: '',
    stepType: '',
    order: stepsList.value.length + 1,
    approvers: [],
    minApprovers: 1,
    timeoutHours: 24,
    escalationAction: '',
    conditionalRule: 'Always Required',
    status: 'Active',
    description: '',
    createdAt: new Date().toISOString().split('T')[0],
    updatedAt: new Date().toISOString().split('T')[0]
  })
  dialogVisible.value = true
}

const handleAddStep = () => {
  handleCreateStep()
}

const viewStep = (step: ApprovalStep) => {
  dialogMode.value = 'view'
  Object.assign(formData, JSON.parse(JSON.stringify(step)))
  dialogVisible.value = true
}

const editStep = (step: ApprovalStep) => {
  dialogMode.value = 'edit'
  Object.assign(formData, JSON.parse(JSON.stringify(step)))
  dialogVisible.value = true
}

const deleteStep = (step: ApprovalStep) => {
  deleteTarget.value = step
  deleteDialogVisible.value = true
}

const moveStepUp = (step: ApprovalStep) => {
  if (!selectedRule.value) return
  const currentOrder = step.order
  const prevStep = selectedRule.value.steps.find(s => s.order === currentOrder - 1)
  if (prevStep) {
    step.order = currentOrder - 1
    prevStep.order = currentOrder
    selectedRule.value.steps.sort((a, b) => a.order - b.order)
    initFlowChart()
    ElMessage.success(`Step "${step.stepName}" moved up`)
  }
}

const moveStepDown = (step: ApprovalStep) => {
  if (!selectedRule.value) return
  const currentOrder = step.order
  const nextStep = selectedRule.value.steps.find(s => s.order === currentOrder + 1)
  if (nextStep) {
    step.order = currentOrder + 1
    nextStep.order = currentOrder
    selectedRule.value.steps.sort((a, b) => a.order - b.order)
    initFlowChart()
    ElMessage.success(`Step "${step.stepName}" moved down`)
  }
}

const confirmDelete = () => {
  if (deleteTarget.value && selectedRule.value) {
    const index = selectedRule.value.steps.findIndex(s => s.id === deleteTarget.value!.id)
    if (index !== -1) {
      selectedRule.value.steps.splice(index, 1)
      // Reorder remaining steps
      selectedRule.value.steps.forEach((step, idx) => {
        step.order = idx + 1
      })
      initFlowChart()
      ElMessage.success(`Deleted: ${deleteTarget.value.stepName}`)
    }
  }
  deleteDialogVisible.value = false
  deleteTarget.value = null
}

const submitForm = async () => {
  if (!formRef.value || !selectedRule.value) return
  await formRef.value.validate((valid: boolean) => {
    if (valid) {
      formData.updatedAt = new Date().toISOString().split('T')[0]

      if (dialogMode.value === 'create') {
        formData.createdAt = new Date().toISOString().split('T')[0]
        formData.order = selectedRule.value!.steps.length + 1
        selectedRule.value!.steps.push({ ...formData, id: Date.now() })
        ElMessage.success('Approval step created successfully')
      } else if (dialogMode.value === 'edit') {
        const index = selectedRule.value!.steps.findIndex(s => s.id === formData.id)
        if (index !== -1) {
          selectedRule.value!.steps[index] = { ...formData }
          ElMessage.success('Approval step updated successfully')
        }
      }
      selectedRule.value!.steps.sort((a, b) => a.order - b.order)
      initFlowChart()
      dialogVisible.value = false
    }
  })
}

// ==================== Loading Simulation ====================
const initCharts = async () => {
  await nextTick()
  setTimeout(() => {
    initFlowChart()
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
      fetchSteps()
    }, 400)
  }, 2000)
})

watch(selectedRuleId, () => {
  initFlowChart()
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
.approval-steps-page {
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

.rule-selector-card {
  margin-bottom: 20px;

  .rule-selector-container {
    display: flex;
    align-items: center;
    gap: 16px;

    .selector-label {
      font-weight: 600;
      color: #303133;
    }
  }
}

.flow-diagram-card {
  margin-bottom: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }
}

.flow-chart-container {
  width: 100%;
  height: 450px;
}

.steps-card {
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

.steps-timeline {
  position: relative;
  padding: 20px 0;

  .step-item {
    display: flex;
    margin-bottom: 24px;
    position: relative;

    &:last-child {
      margin-bottom: 0;

      .step-line {
        display: none;
      }
    }

    .step-marker {
      position: relative;
      width: 60px;
      flex-shrink: 0;
      display: flex;
      flex-direction: column;
      align-items: center;

      .step-number {
        width: 36px;
        height: 36px;
        background: #409eff;
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 16px;
        z-index: 2;
      }

      .step-line {
        position: absolute;
        top: 36px;
        width: 2px;
        height: calc(100% + 8px);
        background: #dcdfe6;
        left: 50%;
        transform: translateX(-50%);
      }
    }

    .step-card {
      flex: 1;
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
      overflow: hidden;
      margin-left: 16px;
      transition: all 0.3s;

      &:hover {
        box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.15);
      }

      .step-header {
        padding: 16px 20px;
        background: #f5f7fa;
        border-bottom: 1px solid #ebeef5;
        display: flex;
        justify-content: space-between;
        align-items: center;

        .step-title {
          display: flex;
          align-items: center;
          gap: 12px;

          .step-name {
            font-weight: 600;
            font-size: 16px;
            color: #303133;
          }
        }

        .step-actions {
          display: flex;
          gap: 8px;
        }
      }

      .step-content {
        padding: 16px 20px;

        .step-info {
          margin-bottom: 8px;
          display: flex;

          .info-label {
            width: 120px;
            font-size: 13px;
            color: #909399;
          }

          .info-value {
            flex: 1;
            font-size: 13px;
            color: #303133;
          }
        }

        .step-description {
          margin-top: 12px;
          padding-top: 12px;
          border-top: 1px solid #ebeef5;
          display: flex;

          .info-label {
            width: 120px;
            font-size: 13px;
            color: #909399;
          }

          .info-value {
            flex: 1;
            font-size: 13px;
            color: #606266;
          }
        }
      }
    }

    &.completed {
      .step-marker .step-number {
        background: #67c23a;
      }
    }
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