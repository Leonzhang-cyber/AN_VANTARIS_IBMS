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
        <div class="loading-tip">BIM Management - Model Validation</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="model-validation-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>Model Validation</h1>
        <p>Validate BIM models against industry standards, project requirements, and clash detection</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="runValidation" :loading="isValidating">
          <el-icon><VideoPlay /></el-icon>
          Run Validation
        </el-button>
        <el-button @click="exportReport">
          <el-icon><Download /></el-icon>
          Export Report
        </el-button>
        <el-button @click="importModel">
          <el-icon><Upload /></el-icon>
          Import Model
        </el-button>
      </div>
    </div>

    <!-- Model Overview -->
    <div class="model-overview-card">
      <div class="card-header">
        <h3>Current Model</h3>
        <el-tag :type="currentModel.valid ? 'success' : 'danger'" size="large">
          {{ currentModel.valid ? 'Valid' : 'Issues Found' }}
        </el-tag>
      </div>
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="model-stat">
            <div class="stat-label">Model Name</div>
            <div class="stat-value">{{ currentModel.name }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="model-stat">
            <div class="stat-label">IFC Version</div>
            <div class="stat-value">{{ currentModel.ifcVersion }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="model-stat">
            <div class="stat-label">Elements</div>
            <div class="stat-value">{{ currentModel.elementCount }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="model-stat">
            <div class="stat-label">Last Validated</div>
            <div class="stat-value">{{ currentModel.lastValidated }}</div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- Validation Tabs -->
    <div class="validation-tabs">
      <el-tabs v-model="activeTab" @tab-click="handleTabChange">
        <el-tab-pane label="Compliance" name="compliance" />
        <el-tab-pane label="Clash Detection" name="clash" />
        <el-tab-pane label="Data Quality" name="quality" />
        <el-tab-pane label="Schema Check" name="schema" />
        <el-tab-pane label="Issues" name="issues" />
      </el-tabs>
    </div>

    <!-- Compliance Tab -->
    <div v-show="activeTab === 'compliance'" class="tab-content">
      <el-row :gutter="20">
        <el-col :xs="24" :lg="8">
          <div class="compliance-card">
            <div class="card-header">
              <h3>Standard Compliance</h3>
            </div>
            <div class="compliance-list">
              <div v-for="standard in complianceStandards" :key="standard.name" class="compliance-item">
                <div class="compliance-header">
                  <span class="standard-name">{{ standard.name }}</span>
                  <el-tag :type="standard.status === 'passed' ? 'success' : standard.status === 'warning' ? 'warning' : 'danger'" size="small">
                    {{ standard.status === 'passed' ? 'Passed' : standard.status === 'warning' ? 'Warning' : 'Failed' }}
                  </el-tag>
                </div>
                <div class="compliance-score">
                  <el-progress :percentage="standard.score" :color="standard.score >= 90 ? '#67c23a' : standard.score >= 70 ? '#e6a23c' : '#f56c6c'" :stroke-width="8" />
                </div>
                <div class="compliance-details">{{ standard.details }}</div>
              </div>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :lg="16">
          <div class="chart-card">
            <div class="card-header">
              <h3>Compliance by Category</h3>
              <el-select v-model="complianceCategory" size="small" style="width: 140px">
                <el-option label="All Categories" value="all" />
                <el-option label="Architecture" value="arch" />
                <el-option label="Structure" value="struct" />
                <el-option label="MEP" value="mep" />
              </el-select>
            </div>
            <div ref="complianceChartRef" class="chart-container"></div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- Clash Detection Tab -->
    <div v-show="activeTab === 'clash'" class="tab-content">
      <el-row :gutter="20">
        <el-col :xs="24" :lg="7">
          <div class="clash-summary-card">
            <div class="card-header">
              <h3>Clash Summary</h3>
            </div>
            <div class="clash-stats">
              <div class="clash-stat critical">
                <div class="stat-value">{{ clashStats.critical }}</div>
                <div class="stat-label">Critical</div>
              </div>
              <div class="clash-stat high">
                <div class="stat-value">{{ clashStats.high }}</div>
                <div class="stat-label">High</div>
              </div>
              <div class="clash-stat medium">
                <div class="stat-value">{{ clashStats.medium }}</div>
                <div class="stat-label">Medium</div>
              </div>
              <div class="clash-stat low">
                <div class="stat-value">{{ clashStats.low }}</div>
                <div class="stat-label">Low</div>
              </div>
            </div>
            <div class="clash-actions">
              <el-button size="small" @click="runClashDetection" :loading="isRunningClash">Run Clash Detection</el-button>
              <el-button size="small" @click="exportClashReport">Export Clash Report</el-button>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :lg="17">
          <div class="clash-list-card">
            <div class="card-header">
              <h3>Clash Groups</h3>
              <el-input v-model="clashSearch" placeholder="Search clashes..." clearable size="small" style="width: 200px" :prefix-icon="Search" />
            </div>
            <el-table :data="filteredClashes" stripe height="350">
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column prop="element1" label="Element 1" min-width="150" />
              <el-table-column prop="element2" label="Element 2" min-width="150" />
              <el-table-column prop="severity" label="Severity" width="100">
                <template #default="{ row }">
                  <el-tag :type="getClashSeverityType(row.severity)" size="small">
                    {{ row.severity }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="type" label="Type" width="100" />
              <el-table-column label="Actions" width="100">
                <template #default="{ row }">
                  <el-button link type="primary" size="small" @click="viewClash(row)">View</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- Data Quality Tab -->
    <div v-show="activeTab === 'quality'" class="tab-content">
      <el-row :gutter="20">
        <el-col :xs="24" :lg="12">
          <div class="quality-card">
            <div class="card-header">
              <h3>Data Quality Metrics</h3>
            </div>
            <div class="quality-metrics">
              <div v-for="metric in qualityMetrics" :key="metric.name" class="metric-item">
                <div class="metric-header">
                  <span>{{ metric.name }}</span>
                  <span class="metric-score">{{ metric.score }}%</span>
                </div>
                <el-progress :percentage="metric.score" :color="metric.score >= 90 ? '#67c23a' : metric.score >= 70 ? '#e6a23c' : '#f56c6c'" :stroke-width="8" />
                <div class="metric-description">{{ metric.description }}</div>
              </div>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :lg="12">
          <div class="chart-card">
            <div class="card-header">
              <h3>Missing Properties by Category</h3>
            </div>
            <div ref="missingPropsChartRef" class="chart-container"></div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- Schema Check Tab -->
    <div v-show="activeTab === 'schema'" class="tab-content">
      <el-row :gutter="20">
        <el-col :xs="24" :lg="8">
          <div class="schema-card">
            <div class="card-header">
              <h3>Schema Validation</h3>
            </div>
            <div class="schema-status" :class="schemaValidation.valid ? 'valid' : 'invalid'">
              <el-icon><component :is="schemaValidation.valid ? 'CircleCheck' : 'CircleClose'" /></el-icon>
              <span>{{ schemaValidation.valid ? 'Schema is valid' : 'Schema validation failed' }}</span>
            </div>
            <div class="schema-details">
              <div class="schema-row">
                <span class="label">IFC Schema:</span>
                <span class="value">{{ schemaValidation.schema }}</span>
              </div>
              <div class="schema-row">
                <span class="label">Entities:</span>
                <span class="value">{{ schemaValidation.entityCount }}</span>
              </div>
              <div class="schema-row">
                <span class="label">Types:</span>
                <span class="value">{{ schemaValidation.typeCount }}</span>
              </div>
              <div class="schema-row">
                <span class="label">Rules Checked:</span>
                <span class="value">{{ schemaValidation.rulesChecked }}</span>
              </div>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :lg="16">
          <div class="schema-issues-card">
            <div class="card-header">
              <h3>Schema Issues</h3>
            </div>
            <el-table :data="schemaIssues" stripe>
              <el-table-column prop="code" label="Code" width="100" />
              <el-table-column prop="entity" label="Entity" width="150" />
              <el-table-column prop="message" label="Message" min-width="300" />
              <el-table-column prop="severity" label="Severity" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.severity === 'error' ? 'danger' : 'warning'" size="small">
                    {{ row.severity }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- Issues Tab -->
    <div v-show="activeTab === 'issues'" class="tab-content">
      <div class="issues-card">
        <div class="card-header">
          <h3>Validation Issues</h3>
          <div class="issue-filters">
            <el-select v-model="issueFilter.severity" placeholder="Severity" clearable size="small" style="width: 120px">
              <el-option label="All" value="" />
              <el-option label="Error" value="error" />
              <el-option label="Warning" value="warning" />
              <el-option label="Info" value="info" />
            </el-select>
            <el-select v-model="issueFilter.category" placeholder="Category" clearable size="small" style="width: 140px">
              <el-option label="All" value="" />
              <el-option label="Compliance" value="compliance" />
              <el-option label="Clash" value="clash" />
              <el-option label="Data Quality" value="quality" />
              <el-option label="Schema" value="schema" />
            </el-select>
            <el-input v-model="issueFilter.search" placeholder="Search..." clearable size="small" style="width: 180px" :prefix-icon="Search" />
          </div>
        </div>
        <el-table :data="filteredIssues" stripe>
          <el-table-column prop="id" label="ID" width="100" />
          <el-table-column prop="title" label="Title" min-width="250" />
          <el-table-column prop="category" label="Category" width="120" />
          <el-table-column prop="severity" label="Severity" width="100">
            <template #default="{ row }">
              <el-tag :type="row.severity === 'error' ? 'danger' : row.severity === 'warning' ? 'warning' : 'info'" size="small">
                {{ row.severity }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="element" label="Element" width="150" />
          <el-table-column label="Actions" width="100">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="viewIssue(row)">Details</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- Validation Progress Dialog -->
    <el-dialog v-model="progressDialog.visible" title="Model Validation in Progress" width="450px" :close-on-click-modal="false" :show-close="false">
      <div class="validation-progress">
        <el-progress :percentage="validationProgress" :stroke-width="10" />
        <div class="progress-steps">
          <div class="step" :class="{ active: currentStep >= 1, completed: currentStep > 1 }">
            <span class="step-num">1</span>
            <span class="step-label">Schema Check</span>
          </div>
          <div class="step" :class="{ active: currentStep >= 2, completed: currentStep > 2 }">
            <span class="step-num">2</span>
            <span class="step-label">Compliance</span>
          </div>
          <div class="step" :class="{ active: currentStep >= 3, completed: currentStep > 3 }">
            <span class="step-num">3</span>
            <span class="step-label">Data Quality</span>
          </div>
          <div class="step" :class="{ active: currentStep >= 4, completed: currentStep > 4 }">
            <span class="step-num">4</span>
            <span class="step-label">Clash Detection</span>
          </div>
        </div>
        <div class="current-status">{{ currentStatus }}</div>
      </div>
    </el-dialog>

    <!-- Issue Detail Dialog -->
    <el-dialog v-model="issueDetailDialog.visible" :title="issueDetailDialog.issue?.title" width="550px">
      <div v-if="issueDetailDialog.issue" class="issue-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Issue ID">{{ issueDetailDialog.issue.id }}</el-descriptions-item>
          <el-descriptions-item label="Category">{{ issueDetailDialog.issue.category }}</el-descriptions-item>
          <el-descriptions-item label="Severity">
            <el-tag :type="issueDetailDialog.issue.severity === 'error' ? 'danger' : issueDetailDialog.issue.severity === 'warning' ? 'warning' : 'info'" size="small">
              {{ issueDetailDialog.issue.severity }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Element">{{ issueDetailDialog.issue.element || 'N/A' }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ issueDetailDialog.issue.description }}</el-descriptions-item>
          <el-descriptions-item label="Recommendation" :span="2">{{ issueDetailDialog.issue.recommendation }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="issueDetailDialog.visible = false">Close</el-button>
        <el-button type="primary" @click="createWorkOrder">Create Work Order</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, nextTick,watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  VideoPlay,
  Download,
  Upload,
  CircleCheck,
  CircleClose,
  Search,
  InfoFilled,
  Warning,
  Document,
  DataLine,
  Grid
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const isValidating = ref(false)
const isRunningClash = ref(false)
const validationProgress = ref(0)
const currentStep = ref(0)
const currentStatus = ref('')
const activeTab = ref('compliance')
const complianceCategory = ref('all')
const clashSearch = ref('')

const loadingMessages = [
  'Preparing...',
  'Loading validation engine...',
  'Initializing checkers...',
  'Almost ready...'
]

// ==================== 模拟数据 ====================
const currentModel = reactive({
  name: 'Headquarters_BIM_Model_v3.2.ifc',
  ifcVersion: 'IFC4x3',
  elementCount: 12456,
  lastValidated: '2024-06-10',
  valid: false
})

const complianceStandards = ref([
  { name: 'ISO 19650', status: 'passed', score: 98, details: 'All requirements met' },
  { name: 'COBie Compliance', status: 'warning', score: 85, details: 'Missing properties in component sheets' },
  { name: 'LOD 300 Requirements', status: 'failed', score: 72, details: 'Insufficient geometry detail in MEP elements' },
  { name: 'BCF Standard', status: 'passed', score: 95, details: 'Issue tracking compliant' },
  { name: 'IFC Schema Validation', status: 'passed', score: 100, details: 'No schema violations' }
])

const clashStats = reactive({
  critical: 3,
  high: 8,
  medium: 15,
  low: 24
})

const clashes = ref([
  { id: 'CL-001', element1: 'Ductwork D-101', element2: 'Structural Beam B-205', severity: 'critical', type: 'Hard Clash' },
  { id: 'CL-002', element1: 'Pipe P-203', element2: 'Electrical Conduit E-101', severity: 'high', type: 'Hard Clash' },
  { id: 'CL-003', element1: 'HVAC Unit AHU-05', element2: 'Fire Sprinkler FS-12', severity: 'critical', type: 'Clearance Clash' },
  { id: 'CL-004', element1: 'Wall W-101', element2: 'Door D-102', severity: 'medium', type: 'Opening Clash' },
  { id: 'CL-005', element1: 'Cable Tray T-01', element2: 'Lighting Fixture L-203', severity: 'high', type: 'Hard Clash' },
  { id: 'CL-006', element1: 'Chilled Water Pipe', element2: 'Structural Column C-102', severity: 'critical', type: 'Penetration Clash' }
])

const qualityMetrics = ref([
  { name: 'Completeness', score: 86, description: 'Percentage of required properties present' },
  { name: 'Consistency', score: 92, description: 'Consistent naming and classification' },
  { name: 'Accuracy', score: 88, description: 'Geometric accuracy and precision' },
  { name: 'Connectivity', score: 76, description: 'Proper connections between elements' },
  { name: 'Classification', score: 91, description: 'Uniclass/OmniClass compliance' }
])

const schemaValidation = reactive({
  valid: true,
  schema: 'IFC4x3',
  entityCount: 342,
  typeCount: 156,
  rulesChecked: 128
})

const schemaIssues = ref([
  { code: 'E-101', entity: 'IfcWall', message: 'Missing Required Property Set: Pset_WallCommon', severity: 'error' },
  { code: 'W-203', entity: 'IfcSlab', message: 'Non-standard attribute value for LoadBearing', severity: 'warning' },
  { code: 'I-045', entity: 'IfcDistributionElement', message: 'Inconsistent GUID format', severity: 'warning' }
])

const validationIssues = ref([
  { id: 'V-001', title: 'Missing fire rating property on all walls', category: 'Compliance', severity: 'error', element: 'IfcWall', description: 'Fire rating property is required for all wall elements per building code.', recommendation: 'Add Pset_WallCommon with FireRating property' },
  { id: 'V-002', title: 'Incorrect IFC class for HVAC equipment', category: 'Schema', severity: 'error', element: 'IfcDistributionElement', description: 'HVAC equipment should use IfcFlowTerminal or IfcFlowController.', recommendation: 'Reclassify elements to appropriate IFC class' },
  { id: 'V-003', title: 'Missing COBie contact information', category: 'Compliance', severity: 'warning', element: 'Project', description: 'COBie required contact information not provided.', recommendation: 'Add contact details to project information' },
  { id: 'V-004', title: 'Duplicate element identifiers', category: 'Quality', severity: 'warning', element: 'Multiple', description: 'Duplicate GUID detected in multiple elements.', recommendation: 'Regenerate unique identifiers' },
  { id: 'V-005', title: 'Unconnected duct system', category: 'Quality', severity: 'error', element: 'Duct D-101', description: 'Duct segment not connected to any terminal.', recommendation: 'Review HVAC system connectivity' },
  { id: 'V-006', title: 'Missing level assignment', category: 'Quality', severity: 'warning', element: 'IfcBuildingElementProxy', description: 'Element not assigned to any building storey.', recommendation: 'Assign elements to appropriate levels' }
])

const progressDialog = reactive({
  visible: false
})

const issueDetailDialog = reactive({
  visible: false,
  issue: null as any
})

const issueFilter = reactive({
  severity: '',
  category: '',
  search: ''
})

// ==================== 图表引用 ====================
const complianceChartRef = ref<HTMLElement | null>(null)
const missingPropsChartRef = ref<HTMLElement | null>(null)

let complianceChart: echarts.ECharts | null = null
let missingPropsChart: echarts.ECharts | null = null

// ==================== 计算属性 ====================
const filteredClashes = computed(() => {
  let filtered = [...clashes.value]
  if (clashSearch.value) {
    const searchLower = clashSearch.value.toLowerCase()
    filtered = filtered.filter(c =>
        c.id.toLowerCase().includes(searchLower) ||
        c.element1.toLowerCase().includes(searchLower) ||
        c.element2.toLowerCase().includes(searchLower)
    )
  }
  return filtered
})

const filteredIssues = computed(() => {
  let filtered = [...validationIssues.value]
  if (issueFilter.severity) {
    filtered = filtered.filter(i => i.severity === issueFilter.severity)
  }
  if (issueFilter.category) {
    filtered = filtered.filter(i => i.category.toLowerCase() === issueFilter.category)
  }
  if (issueFilter.search) {
    const searchLower = issueFilter.search.toLowerCase()
    filtered = filtered.filter(i =>
        i.title.toLowerCase().includes(searchLower) ||
        i.id.toLowerCase().includes(searchLower)
    )
  }
  return filtered
})

// ==================== 辅助函数 ====================
const getClashSeverityType = (severity: string) => {
  const map: Record<string, string> = {
    'critical': 'danger',
    'high': 'danger',
    'medium': 'warning',
    'low': 'info'
  }
  return map[severity] || 'info'
}

// ==================== 图表渲染 ====================
const renderComplianceChart = () => {
  if (!complianceChartRef.value) return
  if (complianceChart) complianceChart.dispose()

  complianceChart = echarts.init(complianceChartRef.value)

  const categories = ['Architecture', 'Structure', 'MEP', 'Fire Safety', 'Security']
  const scores = [92, 88, 76, 85, 90]
  const target = [90, 90, 85, 90, 90]

  complianceChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Current Score', 'Target'], top: 0 },
    xAxis: { type: 'category', data: categories, axisLabel: { rotate: 30 } },
    yAxis: { type: 'value', name: 'Compliance (%)', max: 100 },
    series: [
      { name: 'Current Score', type: 'bar', data: scores, itemStyle: { color: '#409eff', borderRadius: [4, 4, 0, 0] } },
      { name: 'Target', type: 'line', data: target, lineStyle: { color: '#e6a23c', width: 2, type: 'dashed' } }
    ]
  })
}

const renderMissingPropsChart = () => {
  if (!missingPropsChartRef.value) return
  if (missingPropsChart) missingPropsChart.dispose()

  missingPropsChart = echarts.init(missingPropsChartRef.value)

  const categories = ['Walls', 'Slabs', 'Doors', 'Windows', 'HVAC', 'Electrical', 'Plumbing']
  const missingCount = [45, 23, 12, 8, 67, 34, 28]

  missingPropsChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: { type: 'category', data: categories, axisLabel: { rotate: 30 } },
    yAxis: { type: 'value', name: 'Missing Properties' },
    series: [{ type: 'bar', data: missingCount, itemStyle: { color: '#f56c6c', borderRadius: [4, 4, 0, 0] } }]
  })
}

// ==================== 验证模拟 ====================
const runValidation = async () => {
  isValidating.value = true
  progressDialog.visible = true
  validationProgress.value = 0
  currentStep.value = 0

  const steps = [
    { name: 'Schema Check', duration: 1500 },
    { name: 'Compliance Check', duration: 2000 },
    { name: 'Data Quality Check', duration: 1800 },
    { name: 'Clash Detection', duration: 2500 }
  ]

  for (let i = 0; i < steps.length; i++) {
    currentStep.value = i + 1
    currentStatus.value = steps[i].name
    validationProgress.value = ((i) / steps.length) * 100

    await new Promise(resolve => setTimeout(resolve, steps[i].duration))
    validationProgress.value = ((i + 1) / steps.length) * 100
  }

  await new Promise(resolve => setTimeout(resolve, 500))
  progressDialog.visible = false
  isValidating.value = false

  currentModel.valid = validationIssues.value.filter(i => i.severity === 'error').length === 0
  currentModel.lastValidated = new Date().toISOString().slice(0, 10)

  ElMessage.success('Model validation completed')
}

const runClashDetection = async () => {
  isRunningClash.value = true
  await new Promise(resolve => setTimeout(resolve, 2000))
  isRunningClash.value = false
  ElMessage.success('Clash detection completed')
}

const exportReport = () => {
  const report = {
    generatedAt: new Date().toISOString(),
    model: currentModel,
    compliance: complianceStandards.value,
    clashes: clashes.value,
    quality: qualityMetrics.value,
    issues: validationIssues.value
  }
  const data = JSON.stringify(report, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `validation-report-${new Date().toISOString().slice(0, 19)}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Report exported')
}

const exportClashReport = () => {
  const data = JSON.stringify(clashes.value, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `clash-report-${new Date().toISOString().slice(0, 19)}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Clash report exported')
}

const importModel = () => {
  ElMessage.info('Model import functionality - select an IFC file')
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.ifc,.ifcxml'
  input.onchange = (e: any) => {
    if (e.target.files?.[0]) {
      currentModel.name = e.target.files[0].name
      ElMessage.success(`Model ${currentModel.name} imported`)
    }
  }
  input.click()
}

const viewClash = (clash: any) => {
  ElMessage.info(`Viewing clash ${clash.id} - ${clash.element1} vs ${clash.element2}`)
}

const viewIssue = (issue: any) => {
  issueDetailDialog.issue = issue
  issueDetailDialog.visible = true
}

const createWorkOrder = () => {
  ElMessage.success('Work order created for this issue')
  issueDetailDialog.visible = false
}

const handleTabChange = () => {
  nextTick(() => {
    if (activeTab.value === 'compliance') renderComplianceChart()
    if (activeTab.value === 'quality') renderMissingPropsChart()
  })
}

// ==================== 数据加载 ====================
const loadData = () => {
  nextTick(() => {
    renderComplianceChart()
    renderMissingPropsChart()
  })
}

// ==================== 生命周期 ====================
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
      loadData()
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  window.removeEventListener('resize', () => {
    complianceChart?.resize()
    missingPropsChart?.resize()
  })
})

watch(isLoaded, (loaded) => {
  if (loaded) {
    window.addEventListener('resize', () => {
      complianceChart?.resize()
      missingPropsChart?.resize()
    })
  }
})
</script>

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

/* ==================== Main Content Styles ==================== */
.model-validation-page {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
  color: #1f2f3d;
}

.page-header p {
  margin: 0;
  color: #5e6e82;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Cards */
.model-overview-card, .compliance-card, .chart-card, .clash-summary-card,
.clash-list-card, .quality-card, .schema-card, .schema-issues-card, .issues-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2f3d;
}

.model-stat {
  text-align: center;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
}

.model-stat .stat-label {
  font-size: 12px;
  color: #8c9aab;
  margin-bottom: 4px;
}

.model-stat .stat-value {
  font-size: 18px;
  font-weight: 600;
  color: #1f2f3d;
}

/* Validation Tabs */
.validation-tabs {
  background: white;
  border-radius: 12px;
  padding: 0 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.tab-content {
  margin-top: 0;
}

/* Compliance */
.compliance-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.compliance-item {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
}

.compliance-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.standard-name {
  font-weight: 500;
  font-size: 14px;
}

.compliance-details {
  font-size: 11px;
  color: #8c9aab;
  margin-top: 6px;
}

.chart-container {
  height: 320px;
  width: 100%;
}

/* Clash Detection */
.clash-stats {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.clash-stat {
  flex: 1;
  text-align: center;
  padding: 16px;
  border-radius: 8px;
}

.clash-stat.critical { background-color: #fef0f0; }
.clash-stat.high { background-color: #fef0f0; }
.clash-stat.medium { background-color: #fff3e0; }
.clash-stat.low { background-color: #f0f9eb; }

.clash-stat .stat-value {
  font-size: 28px;
  font-weight: 700;
}

.clash-stat.critical .stat-value { color: #f56c6c; }
.clash-stat.high .stat-value { color: #f56c6c; }
.clash-stat.medium .stat-value { color: #e6a23c; }
.clash-stat.low .stat-value { color: #67c23a; }

.clash-stat .stat-label {
  font-size: 12px;
  color: #8c9aab;
}

.clash-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

/* Data Quality */
.quality-metrics {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.metric-item {
  width: 100%;
}

.metric-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  font-size: 13px;
}

.metric-score {
  font-weight: 600;
  color: #1f2f3d;
}

.metric-description {
  font-size: 10px;
  color: #8c9aab;
  margin-top: 4px;
}

/* Schema */
.schema-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.schema-status.valid {
  background-color: #f0f9eb;
  color: #67c23a;
}

.schema-status.invalid {
  background-color: #fef0f0;
  color: #f56c6c;
}

.schema-details {
  padding: 8px 0;
}

.schema-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #ebeef5;
}

.schema-row .label {
  color: #8c9aab;
}

.schema-row .value {
  font-weight: 500;
}

/* Issues */
.issue-filters {
  display: flex;
  gap: 12px;
}

/* Validation Progress */
.validation-progress {
  padding: 20px;
}

.progress-steps {
  display: flex;
  justify-content: space-between;
  margin: 30px 0;
}

.step {
  text-align: center;
  flex: 1;
}

.step-num {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #f0f0f0;
  color: #8c9aab;
  margin-bottom: 8px;
}

.step.active .step-num {
  background: #409eff;
  color: white;
}

.step.completed .step-num {
  background: #67c23a;
  color: white;
}

.step-label {
  font-size: 11px;
  color: #8c9aab;
}

.step.active .step-label {
  color: #409eff;
  font-weight: 500;
}

.current-status {
  text-align: center;
  font-size: 14px;
  color: #409eff;
  margin-top: 16px;
}

/* Issue Detail */
.issue-detail {
  padding: 8px 0;
}

:deep(.el-table th) {
  background-color: #fafbfc;
  font-weight: 600;
}

:deep(.el-tabs__header) {
  margin-bottom: 0;
}
</style>