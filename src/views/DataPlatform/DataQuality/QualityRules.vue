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
        <div class="loading-tip">Data Quality Rules</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="quality-rules-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Data Platform</el-breadcrumb-item>
            <el-breadcrumb-item>Data Quality</el-breadcrumb-item>
            <el-breadcrumb-item>Quality Rules</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Data Quality Rules</h1>
        <p class="description">Define and manage data quality validation rules for completeness, accuracy, consistency, and timeliness</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Rules
        </el-button>
        <el-button type="primary" @click="handleCreateRule">
          <el-icon><Plus /></el-icon>
          Create Rule
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

    <!-- Rule Type Distribution Chart -->
    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :lg="14">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Rule Execution Trend</span>
              <el-radio-group v-model="trendPeriod" size="small">
                <el-radio-button value="weekly">Weekly</el-radio-button>
                <el-radio-button value="monthly">Monthly</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="10">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Rules by Type</span>
            </div>
          </template>
          <div ref="typeChartRef" class="pie-chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Filters -->
    <el-card class="filter-card" shadow="hover">
      <div class="filter-container">
        <div class="filter-row">
          <el-input
              v-model="filters.keyword"
              placeholder="Search by rule name or description"
              prefix-icon="Search"
              clearable
              style="width: 240px"
              @clear="handleSearch"
              @keyup.enter="handleSearch"
          />
          <el-select v-model="filters.ruleType" placeholder="Rule Type" clearable style="width: 140px">
            <el-option label="Completeness" value="Completeness" />
            <el-option label="Accuracy" value="Accuracy" />
            <el-option label="Consistency" value="Consistency" />
            <el-option label="Timeliness" value="Timeliness" />
            <el-option label="Uniqueness" value="Uniqueness" />
            <el-option label="Validity" value="Validity" />
          </el-select>
          <el-select v-model="filters.severity" placeholder="Severity" clearable style="width: 120px">
            <el-option label="Critical" value="Critical" />
            <el-option label="High" value="High" />
            <el-option label="Medium" value="Medium" />
            <el-option label="Low" value="Low" />
          </el-select>
          <el-select v-model="filters.status" placeholder="Status" clearable style="width: 120px">
            <el-option label="Active" value="Active" />
            <el-option label="Inactive" value="Inactive" />
            <el-option label="Draft" value="Draft" />
          </el-select>
          <el-button type="primary" @click="handleSearch">Search</el-button>
          <el-button @click="handleResetFilters">Reset</el-button>
        </div>
      </div>
    </el-card>

    <!-- Rules Table -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Quality Rules ({{ filteredRules.length }} rules)</span>
          <div class="table-actions">
            <el-button :icon="Refresh" @click="fetchRules" circle />
            <el-button :icon="Setting" @click="handleColumnSettings" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedRules" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="name" label="Rule Name" min-width="200" show-overflow-tooltip />
        <el-table-column prop="ruleType" label="Type" width="120">
          <template #default="{ row }">
            <el-tag :type="getRuleTypeTag(row.ruleType)" size="small">{{ row.ruleType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="targetColumn" label="Target Column" width="150" show-overflow-tooltip />
        <el-table-column prop="severity" label="Severity" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityTag(row.severity)" size="small">{{ row.severity }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="threshold" label="Threshold" width="100" align="center">
          <template #default="{ row }">
            {{ row.threshold }}%
          </template>
        </el-table-column>
        <el-table-column prop="passRate" label="Pass Rate" width="120">
          <template #default="{ row }">
            <el-progress :percentage="row.passRate" :stroke-width="8" :color="getPassRateColor(row.passRate)" />
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Active' ? 'success' : 'info'" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastRun" label="Last Run" width="160" />
        <el-table-column label="Actions" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewRule(row)">View</el-button>
            <el-button link type="success" size="small" @click="editRule(row)">Edit</el-button>
            <el-button link type="info" size="small" @click="runRule(row)">Run</el-button>
            <el-button link type="danger" size="small" @click="deleteRule(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[15, 30, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredRules.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Create/Edit Rule Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogMode === 'create' ? 'Create Quality Rule' : 'Edit Quality Rule'" width="650px" destroy-on-close>
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="130px">
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="Rule Name" prop="name">
              <el-input v-model="formData.name" placeholder="Enter rule name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Rule Type" prop="ruleType">
              <el-select v-model="formData.ruleType" placeholder="Select rule type" style="width: 100%">
                <el-option label="Completeness" value="Completeness" />
                <el-option label="Accuracy" value="Accuracy" />
                <el-option label="Consistency" value="Consistency" />
                <el-option label="Timeliness" value="Timeliness" />
                <el-option label="Uniqueness" value="Uniqueness" />
                <el-option label="Validity" value="Validity" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Severity" prop="severity">
              <el-select v-model="formData.severity" placeholder="Select severity" style="width: 100%">
                <el-option label="Critical" value="Critical" />
                <el-option label="High" value="High" />
                <el-option label="Medium" value="Medium" />
                <el-option label="Low" value="Low" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Target Table" prop="targetTable">
              <el-select v-model="formData.targetTable" placeholder="Select table" style="width: 100%">
                <el-option label="device_master" value="device_master" />
                <el-option label="energy_consumption" value="energy_consumption" />
                <el-option label="customer_contract" value="customer_contract" />
                <el-option label="maintenance_work_orders" value="maintenance_work_orders" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Target Column" prop="targetColumn">
              <el-input v-model="formData.targetColumn" placeholder="Enter column name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Threshold (%)" prop="threshold">
              <el-input-number v-model="formData.threshold" :min="0" :max="100" :step="5" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Schedule" prop="schedule">
              <el-select v-model="formData.schedule" placeholder="Select schedule" style="width: 100%">
                <el-option label="Hourly" value="Hourly" />
                <el-option label="Daily" value="Daily" />
                <el-option label="Weekly" value="Weekly" />
                <el-option label="Monthly" value="Monthly" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="Rule Expression" prop="expression">
              <el-input v-model="formData.expression" type="textarea" :rows="2" placeholder="e.g., column IS NOT NULL" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="Description" prop="description">
              <el-input v-model="formData.description" type="textarea" :rows="2" placeholder="Enter rule description" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="testRule">Test Rule</el-button>
        <el-button type="success" @click="submitForm">Save Rule</el-button>
      </template>
    </el-dialog>

    <!-- Rule Details Dialog -->
    <el-dialog v-model="detailsDialogVisible" :title="currentRule?.name" width="700px" destroy-on-close>
      <div class="rule-details" v-if="currentRule">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Rule Name">{{ currentRule.name }}</el-descriptions-item>
          <el-descriptions-item label="Rule Type">
            <el-tag :type="getRuleTypeTag(currentRule.ruleType)" size="small">{{ currentRule.ruleType }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Severity">
            <el-tag :type="getSeverityTag(currentRule.severity)" size="small">{{ currentRule.severity }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="currentRule.status === 'Active' ? 'success' : 'info'" size="small">{{ currentRule.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Target Table">{{ currentRule.targetTable }}</el-descriptions-item>
          <el-descriptions-item label="Target Column">{{ currentRule.targetColumn }}</el-descriptions-item>
          <el-descriptions-item label="Threshold">{{ currentRule.threshold }}%</el-descriptions-item>
          <el-descriptions-item label="Pass Rate">
            <el-progress :percentage="currentRule.passRate" :stroke-width="10" :color="getPassRateColor(currentRule.passRate)" />
          </el-descriptions-item>
          <el-descriptions-item label="Schedule">{{ currentRule.schedule }}</el-descriptions-item>
          <el-descriptions-item label="Last Run">{{ currentRule.lastRun }}</el-descriptions-item>
          <el-descriptions-item label="Rule Expression" :span="2">
            <code class="expression-code">{{ currentRule.expression }}</code>
          </el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ currentRule.description }}</el-descriptions-item>
        </el-descriptions>

        <div class="rule-history">
          <h4>Recent Violations</h4>
          <el-table :data="currentRule.violations || []" size="small" border>
            <el-table-column prop="timestamp" label="Timestamp" width="160" />
            <el-table-column prop="recordId" label="Record ID" width="120" />
            <el-table-column prop="field" label="Field" width="150" />
            <el-table-column prop="value" label="Value" min-width="150" />
            <el-table-column prop="reason" label="Reason" min-width="200" />
          </el-table>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailsDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="runRule(currentRule)">Run Now</el-button>
      </template>
    </el-dialog>

    <!-- Test Result Dialog -->
    <el-dialog v-model="testDialogVisible" title="Rule Test Result" width="500px">
      <div class="test-result">
        <el-result
            :icon="testResult.success ? 'success' : 'error'"
            :title="testResult.success ? 'Test Passed' : 'Test Failed'"
            :sub-title="testResult.message"
        />
        <div class="test-details" v-if="testResult.details">
          <p><strong>Records Scanned:</strong> {{ testResult.details.scanned }}</p>
          <p><strong>Violations Found:</strong> {{ testResult.details.violations }}</p>
          <p><strong>Pass Rate:</strong> {{ testResult.details.passRate }}%</p>
          <p><strong>Execution Time:</strong> {{ testResult.details.executionTime }}ms</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="testDialogVisible = false">Close</el-button>
        <el-button v-if="testResult.success && dialogMode !== 'view'" type="primary" @click="saveAfterTest">Save Rule</el-button>
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
  Clock, TrendCharts, Refresh, Search, Download, Setting,
  DataAnalysis, Filter, Warning
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading quality rules...',
  'Initializing validators...',
  'Almost ready...'
]

// ==================== Chart References ====================
const trendChartRef = ref<HTMLElement>()
const typeChartRef = ref<HTMLElement>()
let trendChart: echarts.ECharts | null = null
let typeChart: echarts.ECharts | null = null

// ==================== State ====================
const tableLoading = ref(false)
const dialogVisible = ref(false)
const detailsDialogVisible = ref(false)
const testDialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const currentRule = ref<any>(null)
const formRef = ref()
const currentPage = ref(1)
const pageSize = ref(15)
const trendPeriod = ref('weekly')

const filters = reactive({
  keyword: '',
  ruleType: '',
  severity: '',
  status: ''
})

const testResult = reactive({
  success: false,
  message: '',
  details: null as any
})

const formData = reactive({
  name: '',
  ruleType: '',
  severity: 'Medium',
  targetTable: '',
  targetColumn: '',
  threshold: 95,
  schedule: 'Daily',
  expression: '',
  description: '',
  status: 'Active'
})

const formRules = {
  name: [{ required: true, message: 'Please enter rule name', trigger: 'blur' }],
  ruleType: [{ required: true, message: 'Please select rule type', trigger: 'change' }],
  targetTable: [{ required: true, message: 'Please select target table', trigger: 'change' }],
  targetColumn: [{ required: true, message: 'Please enter target column', trigger: 'blur' }],
  expression: [{ required: true, message: 'Please enter rule expression', trigger: 'blur' }]
}

// ==================== Mock Data ====================
const statsCards = ref([
  { title: 'Total Rules', value: 48, trend: 12, icon: 'Document', bgColor: '#409eff', key: 'total' },
  { title: 'Active Rules', value: 36, trend: 8, icon: 'Checked', bgColor: '#67c23a', key: 'active' },
  { title: 'Avg Pass Rate', value: '87%', trend: 3, icon: 'TrendCharts', bgColor: '#e6a23c', key: 'passRate' },
  { title: 'Open Violations', value: 156, trend: -5, icon: 'Warning', bgColor: '#f56c6c', key: 'violations' }
])

const qualityRules = ref([
  {
    id: 1,
    name: 'Device Location Completeness',
    ruleType: 'Completeness',
    targetTable: 'device_master',
    targetColumn: 'location',
    severity: 'High',
    threshold: 98,
    passRate: 85,
    status: 'Active',
    schedule: 'Daily',
    lastRun: '2024-01-20 01:00:00',
    expression: 'location IS NOT NULL AND location != \'\'',
    description: 'Ensures all devices have a valid location assigned',
    violations: [
      { timestamp: '2024-01-20 01:00:00', recordId: 'DEV-045', field: 'location', value: 'NULL', reason: 'Missing location information' },
      { timestamp: '2024-01-20 01:00:00', recordId: 'DEV-078', field: 'location', value: 'NULL', reason: 'Missing location information' }
    ]
  },
  {
    id: 2,
    name: 'Energy Consumption Positive Values',
    ruleType: 'Validity',
    targetTable: 'energy_consumption',
    targetColumn: 'consumption_kwh',
    severity: 'Critical',
    threshold: 100,
    passRate: 92,
    status: 'Active',
    schedule: 'Daily',
    lastRun: '2024-01-20 02:00:00',
    expression: 'consumption_kwh > 0',
    description: 'Energy consumption values must be positive numbers',
    violations: [
      { timestamp: '2024-01-20 02:00:00', recordId: 'REC-1023', field: 'consumption_kwh', value: '-45.2', reason: 'Negative consumption value' }
    ]
  },
  {
    id: 3,
    name: 'Device ID Uniqueness',
    ruleType: 'Uniqueness',
    targetTable: 'device_master',
    targetColumn: 'device_id',
    severity: 'Critical',
    threshold: 100,
    passRate: 100,
    status: 'Active',
    schedule: 'Daily',
    lastRun: '2024-01-20 01:00:00',
    expression: 'COUNT(DISTINCT device_id) = COUNT(device_id)',
    description: 'Device IDs must be unique across the table',
    violations: []
  },
  {
    id: 4,
    name: 'Timestamp Recency Check',
    ruleType: 'Timeliness',
    targetTable: 'energy_consumption',
    targetColumn: 'timestamp',
    severity: 'Medium',
    threshold: 95,
    passRate: 98,
    status: 'Active',
    schedule: 'Hourly',
    lastRun: '2024-01-20 10:00:00',
    expression: 'timestamp >= CURRENT_DATE - INTERVAL \'1 day\'',
    description: 'Energy data must be ingested within 24 hours',
    violations: []
  },
  {
    id: 5,
    name: 'Contract Date Consistency',
    ruleType: 'Consistency',
    targetTable: 'customer_contract',
    targetColumn: 'end_date',
    severity: 'High',
    threshold: 98,
    passRate: 96,
    status: 'Active',
    schedule: 'Weekly',
    lastRun: '2024-01-19 03:00:00',
    expression: 'end_date > start_date',
    description: 'Contract end date must be after start date',
    violations: [
      { timestamp: '2024-01-19 03:00:00', recordId: 'CT-089', field: 'end_date', value: '2023-12-31', reason: 'End date before start date' }
    ]
  },
  {
    id: 6,
    name: 'Device Status Validity',
    ruleType: 'Validity',
    targetTable: 'device_master',
    targetColumn: 'status',
    severity: 'Medium',
    threshold: 100,
    passRate: 99,
    status: 'Active',
    schedule: 'Daily',
    lastRun: '2024-01-20 01:00:00',
    expression: 'status IN (\'active\', \'maintenance\', \'offline\')',
    description: 'Device status must be from allowed list',
    violations: []
  }
])

// ==================== Computed ====================
const filteredRules = computed(() => {
  let filtered = [...qualityRules.value]

  if (filters.keyword) {
    filtered = filtered.filter(r =>
        r.name.toLowerCase().includes(filters.keyword.toLowerCase()) ||
        r.description.toLowerCase().includes(filters.keyword.toLowerCase())
    )
  }

  if (filters.ruleType) {
    filtered = filtered.filter(r => r.ruleType === filters.ruleType)
  }

  if (filters.severity) {
    filtered = filtered.filter(r => r.severity === filters.severity)
  }

  if (filters.status) {
    filtered = filtered.filter(r => r.status === filters.status)
  }

  return filtered
})

const paginatedRules = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredRules.value.slice(start, end)
})

// ==================== Helper Methods ====================
const getRuleTypeTag = (type: string) => {
  const map: Record<string, string> = {
    'Completeness': 'primary',
    'Accuracy': 'success',
    'Consistency': 'warning',
    'Timeliness': 'info',
    'Uniqueness': 'danger',
    'Validity': 'success'
  }
  return map[type] || 'info'
}

const getSeverityTag = (severity: string) => {
  const map: Record<string, string> = {
    'Critical': 'danger',
    'High': 'warning',
    'Medium': 'info',
    'Low': 'success'
  }
  return map[severity] || 'info'
}

const getPassRateColor = (rate: number) => {
  if (rate >= 95) return '#67c23a'
  if (rate >= 80) return '#e6a23c'
  return '#f56c6c'
}

// ==================== Chart Initializations ====================
const initTrendChart = () => {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()

  trendChart = echarts.init(trendChartRef.value)

  const weeklyData = [234, 256, 278, 245, 289, 312, 298, 325, 342, 356, 378, 365]
  const monthlyData = [987, 1023, 1123, 1245, 1342, 1456, 1567, 1678]
  const data = trendPeriod.value === 'weekly' ? weeklyData : monthlyData
  const xAxisData = trendPeriod.value === 'weekly'
      ? ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7', 'Week 8', 'Week 9', 'Week 10', 'Week 11', 'Week 12']
      : ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug']

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: xAxisData },
    yAxis: { type: 'value', name: 'Rules Executed' },
    series: [{
      type: 'line',
      data: data,
      smooth: true,
      lineStyle: { width: 3, color: '#409eff' },
      areaStyle: { opacity: 0.1 },
      symbolSize: 8
    }]
  }

  trendChart.setOption(option)
  window.addEventListener('resize', () => trendChart?.resize())
}

const initTypeChart = () => {
  if (!typeChartRef.value) return
  if (typeChart) typeChart.dispose()

  typeChart = echarts.init(typeChartRef.value)

  const typeCount = {
    'Completeness': qualityRules.value.filter(r => r.ruleType === 'Completeness').length,
    'Accuracy': qualityRules.value.filter(r => r.ruleType === 'Accuracy').length,
    'Consistency': qualityRules.value.filter(r => r.ruleType === 'Consistency').length,
    'Timeliness': qualityRules.value.filter(r => r.ruleType === 'Timeliness').length,
    'Uniqueness': qualityRules.value.filter(r => r.ruleType === 'Uniqueness').length,
    'Validity': qualityRules.value.filter(r => r.ruleType === 'Validity').length
  }

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c} rules)' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: '55%',
      data: [
        { value: typeCount['Completeness'], name: 'Completeness', itemStyle: { color: '#409eff' } },
        { value: typeCount['Accuracy'], name: 'Accuracy', itemStyle: { color: '#67c23a' } },
        { value: typeCount['Consistency'], name: 'Consistency', itemStyle: { color: '#e6a23c' } },
        { value: typeCount['Timeliness'], name: 'Timeliness', itemStyle: { color: '#909399' } },
        { value: typeCount['Uniqueness'], name: 'Uniqueness', itemStyle: { color: '#f56c6c' } },
        { value: typeCount['Validity'], name: 'Validity', itemStyle: { color: '#67c23a' } }
      ],
      emphasis: { scale: true },
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  }

  typeChart.setOption(option)
  window.addEventListener('resize', () => typeChart?.resize())
}

// ==================== Interactive Methods ====================
const handleCardClick = (stat: any) => {
  ElMessage.info(`Viewing ${stat.title} details`)
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleResetFilters = () => {
  filters.keyword = ''
  filters.ruleType = ''
  filters.severity = ''
  filters.status = ''
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

const handleExport = () => {
  ElMessage.success(`Exporting ${filteredRules.value.length} quality rules...`)
}

const handleColumnSettings = () => {
  ElMessage.info('Column settings dialog would open here')
}

const fetchRules = () => {
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
    ElMessage.success('Rules refreshed')
  }, 500)
}

const handleCreateRule = () => {
  dialogMode.value = 'create'
  Object.assign(formData, {
    name: '',
    ruleType: '',
    severity: 'Medium',
    targetTable: '',
    targetColumn: '',
    threshold: 95,
    schedule: 'Daily',
    expression: '',
    description: '',
    status: 'Active'
  })
  dialogVisible.value = true
}

const viewRule = (rule: any) => {
  currentRule.value = rule
  detailsDialogVisible.value = true
}

const editRule = (rule: any) => {
  dialogMode.value = 'edit'
  Object.assign(formData, rule)
  dialogVisible.value = true
}

const testRule = () => {
  // Simulate rule test
  setTimeout(() => {
    const randomPassRate = Math.floor(Math.random() * 30) + 70
    testResult.success = randomPassRate >= (formData.threshold || 95)
    testResult.message = testResult.success
        ? 'Rule validation passed with acceptable quality score'
        : 'Rule validation failed. Quality score below threshold.'
    testResult.details = {
      scanned: Math.floor(Math.random() * 10000) + 1000,
      violations: testResult.success ? Math.floor(Math.random() * 50) : Math.floor(Math.random() * 200) + 100,
      passRate: randomPassRate,
      executionTime: Math.floor(Math.random() * 500) + 100
    }
    testDialogVisible.value = true
  }, 1000)
}

const saveAfterTest = () => {
  testDialogVisible.value = false
  submitForm()
}

const runRule = (rule: any) => {
  ElMessage.info(`Executing rule "${rule.name}"...`)
  setTimeout(() => {
    ElMessage.success(`Rule "${rule.name}" execution completed`)
  }, 1500)
}

const deleteRule = (rule: any) => {
  ElMessageBox.confirm(`Delete rule "${rule.name}"?`, 'Confirm Delete', {
    confirmButtonText: 'Delete',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    const index = qualityRules.value.findIndex(r => r.id === rule.id)
    if (index !== -1) {
      qualityRules.value.splice(index, 1)
      ElMessage.success(`Deleted: ${rule.name}`)
      initTypeChart()
    }
  }).catch(() => {})
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate((valid: boolean) => {
    if (valid) {
      if (dialogMode.value === 'create') {
        const newRule = {
          id: Date.now(),
          ...formData,
          passRate: 100,
          lastRun: 'Never',
          violations: []
        }
        qualityRules.value.unshift(newRule)
        ElMessage.success('Quality rule created successfully')
      } else {
        const index = qualityRules.value.findIndex(r => r.id === formData.id)
        if (index !== -1) {
          qualityRules.value[index] = { ...qualityRules.value[index], ...formData }
          ElMessage.success('Quality rule updated successfully')
        }
      }
      dialogVisible.value = false
      formRef.value?.resetFields()
      initTypeChart()
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
    initTrendChart()
    initTypeChart()
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
      fetchRules()
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
.quality-rules-page {
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

.pie-chart-container {
  width: 100%;
  height: 300px;
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

.rule-details {
  .rule-history {
    margin-top: 20px;

    h4 {
      margin-bottom: 12px;
      color: #303133;
    }
  }

  .expression-code {
    background: #f5f7fa;
    padding: 8px;
    border-radius: 4px;
    font-family: monospace;
    display: block;
  }
}

.test-result {
  .test-details {
    margin-top: 20px;
    padding: 16px;
    background: #f5f7fa;
    border-radius: 8px;

    p {
      margin: 8px 0;
    }
  }
}

:deep(.el-table) {
  font-size: 13px;
}

:deep(.el-dialog__body) {
  max-height: 60vh;
  overflow-y: auto;
}
</style>