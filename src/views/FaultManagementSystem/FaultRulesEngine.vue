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
        <div class="loading-tip">Fault Rules Engine</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Fault Rules Engine Page Content -->
  <div v-else class="fault-rules-engine-page">
    <!-- 页面头部保持不变 -->
    <div class="page-header">
      <div class="header-title">
        <div class="title-badge">
          <el-icon><Setting /></el-icon>
          <span>FMS - Rules Engine</span>
        </div>
        <h1>Fault Rules Engine</h1>
        <p class="subtitle">Configure and manage fault detection rules, thresholds, and automated response actions</p>
      </div>
      <div class="header-actions">
        <button class="action-btn" @click="refreshData">
          <el-icon><Refresh /></el-icon>
          <span>Refresh</span>
        </button>
        <button class="action-btn primary" @click="openCreateRuleDialog">
          <el-icon><Plus /></el-icon>
          <span>Create Rule</span>
        </button>
        <button class="action-btn" @click="testAllRules">
          <el-icon><TrendCharts /></el-icon>
          <span>Test All Rules</span>
        </button>
      </div>
    </div>

    <!-- KPI Summary Cards -->
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-icon total">
          <el-icon><Document /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ totalRules }}</div>
          <div class="kpi-label">Total Rules</div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon active">
          <el-icon><CircleCheckFilled /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ activeRules }}</div>
          <div class="kpi-label">Active Rules</div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon triggered">
          <el-icon><WarningFilled /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ triggeredCount }}</div>
          <div class="kpi-label">Triggered (24h)</div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon accuracy">
          <el-icon><Medal /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ accuracy }}%</div>
          <div class="kpi-label">Rule Accuracy</div>
        </div>
      </div>
    </div>

    <!-- Rule Categories Tabs -->
    <div class="tabs-card">
      <el-tabs v-model="activeTab" @tab-click="handleTabChange">
        <el-tab-pane label="All Rules" name="all" />
        <el-tab-pane label="Threshold Rules" name="threshold" />
        <el-tab-pane label="Status Rules" name="status" />
        <el-tab-pane label="Temporal Rules" name="temporal" />
        <el-tab-pane label="Composite Rules" name="composite" />
      </el-tabs>
    </div>

    <!-- Filters -->
    <div class="filters-bar">
      <div class="filter-group">
        <label>Severity</label>
        <select v-model="filters.severity" class="filter-select">
          <option value="all">All Severities</option>
          <option value="critical">Critical</option>
          <option value="major">Major</option>
          <option value="minor">Minor</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Status</label>
        <select v-model="filters.status" class="filter-select">
          <option value="all">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Category</label>
        <select v-model="filters.category" class="filter-select">
          <option value="all">All Categories</option>
          <option value="HVAC">HVAC</option>
          <option value="Electrical">Electrical</option>
          <option value="Plumbing">Plumbing</option>
          <option value="Security">Security</option>
          <option value="DCIM">DCIM</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Search</label>
        <input type="text" v-model="filters.search" placeholder="Search rules..." class="search-input" />
      </div>
    </div>

    <!-- Rules Table -->
    <div class="table-card">
      <el-table :data="paginatedRules" stripe v-loading="tableLoading" style="width: 100%">
        <el-table-column prop="name" label="Rule Name" min-width="180" show-overflow-tooltip />
        <el-table-column prop="type" label="Type" width="120">
          <template #default="{ row }">
            <el-tag :type="getRuleTypeTag(row.type)" size="small">{{ getRuleTypeLabel(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="condition" label="Condition" min-width="220" show-overflow-tooltip />
        <el-table-column prop="action" label="Action" min-width="150" show-overflow-tooltip />
        <el-table-column prop="severity" label="Severity" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityTag(row.severity)" size="small" effect="dark">
              {{ row.severity.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-switch v-model="row.status" active-value="active" inactive-value="inactive" @change="toggleRuleStatus(row)" />
          </template>
        </el-table-column>
        <el-table-column prop="triggerCount" label="Triggers" width="100" align="center" sortable />
        <el-table-column label="Actions" width="140" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="editRule(row)">Edit</el-button>
            <el-button link type="success" size="small" @click="openTestDialog(row)">Test</el-button>
            <el-button link type="danger" size="small" @click="deleteRule(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredRules.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Rule Statistics - 确保图表容器有明确高度 -->
    <div class="stats-card">
      <div class="card-header">
        <h3>Rule Execution Statistics</h3>
        <el-radio-group v-model="statsPeriod" size="small" @change="onStatsPeriodChange">
          <el-radio-button label="day">Last 24h</el-radio-button>
          <el-radio-button label="week">Last 7 Days</el-radio-button>
          <el-radio-button label="month">Last 30 Days</el-radio-button>
        </el-radio-group>
      </div>
      <div class="stats-chart-wrapper">
        <div class="stats-chart" ref="statsChartRef" style="width: 100%; height: 360px;"></div>
      </div>
    </div>

    <!-- Create/Edit Rule Dialog -->
    <el-dialog v-model="ruleDialogVisible" :title="editingRule ? 'Edit Rule' : 'Create New Rule'" width="700px">
      <el-form :model="ruleForm" label-width="100px">
        <el-form-item label="Rule Name" required>
          <el-input v-model="ruleForm.name" placeholder="e.g., Chiller High Pressure Rule" />
        </el-form-item>
        <el-form-item label="Rule Type" required>
          <el-select v-model="ruleForm.type" style="width: 100%">
            <el-option label="Threshold Rule" value="threshold" />
            <el-option label="Status Rule" value="status" />
            <el-option label="Temporal Rule" value="temporal" />
            <el-option label="Composite Rule" value="composite" />
          </el-select>
        </el-form-item>
        <el-form-item label="Condition" required>
          <el-input type="textarea" v-model="ruleForm.condition" rows="2" placeholder="e.g., chiller.pressure > 200 AND cooling_tower.fan_status == 'OFF'" />
        </el-form-item>
        <el-form-item label="Action" required>
          <el-input type="textarea" v-model="ruleForm.action" rows="2" placeholder="e.g., Create fault CRITICAL with title 'Chiller High Pressure'" />
        </el-form-item>
        <el-form-item label="Severity">
          <el-select v-model="ruleForm.severity" style="width: 100%">
            <el-option label="Critical" value="critical" />
            <el-option label="Major" value="major" />
            <el-option label="Minor" value="minor" />
          </el-select>
        </el-form-item>
        <el-form-item label="Category">
          <el-select v-model="ruleForm.category" style="width: 100%">
            <el-option label="HVAC" value="HVAC" />
            <el-option label="Electrical" value="Electrical" />
            <el-option label="Plumbing" value="Plumbing" />
            <el-option label="Security" value="Security" />
            <el-option label="DCIM" value="DCIM" />
          </el-select>
        </el-form-item>
        <el-form-item label="Priority">
          <el-slider v-model="ruleForm.priority" :min="1" :max="10" :marks="{ 1: 'Low', 5: 'Medium', 10: 'High' }" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="ruleDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveRule">Save Rule</el-button>
      </template>
    </el-dialog>

    <!-- Test Rule Dialog -->
    <el-dialog v-model="testDialogVisible" title="Test Rule" width="500px">
      <div class="test-content">
        <div class="test-rule-name">{{ selectedTestRule?.name }}</div>
        <div class="test-condition">Condition: {{ selectedTestRule?.condition }}</div>
        <div class="test-input">
          <label>Test Input (JSON format):</label>
          <textarea v-model="testInputData" rows="5" placeholder='{"chiller": {"pressure": 220, "status": "running"}, "cooling_tower": {"fan_status": "OFF"}}' class="test-textarea"></textarea>
        </div>
        <div class="test-result" v-if="testResultData">
          <div class="result-title">Test Result:</div>
          <div class="result-status" :class="testResultData.matched ? 'matched' : 'not-matched'">
            {{ testResultData.matched ? '✓ Rule Matched' : '✗ Rule Not Matched' }}
          </div>
          <div class="result-action" v-if="testResultData.action">Action: {{ testResultData.action }}</div>
        </div>
      </div>
      <template #footer>
        <el-button @click="testDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="executeTest">Run Test</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import {
  Refresh, Download, Setting, Plus, TrendCharts, Document,
  CircleCheckFilled, WarningFilled, Medal, Edit, Delete
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'

// Loading State
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const tableLoading = ref(false)
const loadingMessages = ['Preparing...', 'Loading rules engine...', 'Initializing rule sets...', 'Almost ready...']

// Data Models
interface Rule {
  id: number
  name: string
  type: 'threshold' | 'status' | 'temporal' | 'composite'
  condition: string
  action: string
  severity: 'critical' | 'major' | 'minor'
  category: string
  status: 'active' | 'inactive'
  priority: number
  triggerCount: number
  createdAt: string
}

// State
const activeTab = ref('all')
const statsPeriod = ref('week')
const filters = ref({
  severity: 'all',
  status: 'all',
  category: 'all',
  search: ''
})
const currentPage = ref(1)
const pageSize = ref(10)
const ruleDialogVisible = ref(false)
const testDialogVisible = ref(false)
const editingRule = ref<Rule | null>(null)
const selectedTestRule = ref<Rule | null>(null)
const testInputData = ref('')
const testResultData = ref<any>(null)

// Chart refs
const statsChartRef = ref<HTMLElement | null>(null)
let statsChart: echarts.ECharts | null = null

// 图表数据
const chartDataMap = {
  day: {
    xAxis: ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00'],
    triggered: [2, 1, 0, 3, 8, 12, 15, 18, 14, 10, 6, 4],
    resolved: [1, 0, 0, 2, 6, 10, 12, 15, 12, 8, 5, 3]
  },
  week: {
    xAxis: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    triggered: [12, 15, 18, 22, 20, 8, 5],
    resolved: [10, 12, 15, 18, 16, 7, 4]
  },
  month: {
    xAxis: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    triggered: [45, 52, 58, 42],
    resolved: [38, 44, 50, 36]
  }
}

// Mock Data - Rules
const rules = ref<Rule[]>([
  { id: 1, name: 'Chiller High Pressure Rule', type: 'threshold', condition: 'chiller.pressure > 200', action: 'Create CRITICAL fault for Chiller', severity: 'critical', category: 'HVAC', status: 'active', priority: 9, triggerCount: 12, createdAt: '2025-05-01' },
  { id: 2, name: 'Cooling Tower Fan Failure', type: 'status', condition: 'cooling_tower.fan_status == "OFF" AND chiller.status == "running"', action: 'Create MAJOR fault and trigger alert', severity: 'major', category: 'HVAC', status: 'active', priority: 8, triggerCount: 8, createdAt: '2025-05-01' },
  { id: 3, name: 'UPS Input Power Loss', type: 'status', condition: 'ups.input_voltage == 0', action: 'Create CRITICAL fault and notify admin', severity: 'critical', category: 'Electrical', status: 'active', priority: 10, triggerCount: 5, createdAt: '2025-05-02' },
  { id: 4, name: 'Server Room High Temperature', type: 'threshold', condition: 'server_room.temperature > 28', action: 'Create CRITICAL fault for Cooling', severity: 'critical', category: 'DCIM', status: 'active', priority: 9, triggerCount: 6, createdAt: '2025-05-02' },
  { id: 5, name: 'VFD Overcurrent Rule', type: 'threshold', condition: 'vfd.current > vfd.rated_current * 1.2', action: 'Create MAJOR fault for VFD', severity: 'major', category: 'Electrical', status: 'active', priority: 7, triggerCount: 4, createdAt: '2025-05-03' },
  { id: 6, name: 'Water Leak Detection', type: 'status', condition: 'water_sensor.status == "WET"', action: 'Create MAJOR fault for Plumbing', severity: 'major', category: 'Plumbing', status: 'inactive', priority: 8, triggerCount: 2, createdAt: '2025-05-03' },
  { id: 7, name: 'BMS Gateway Offline', type: 'status', condition: 'bms.gateway.status == "OFFLINE" FOR 5 MINUTES', action: 'Create MINOR fault and attempt restart', severity: 'minor', category: 'BMS', status: 'active', priority: 6, triggerCount: 3, createdAt: '2025-05-04' },
  { id: 8, name: 'AHU Filter Clog', type: 'threshold', condition: 'ahu.pressure_differential > 150', action: 'Create MINOR fault for Maintenance', severity: 'minor', category: 'HVAC', status: 'active', priority: 5, triggerCount: 10, createdAt: '2025-05-04' }
])

// Computed
const totalRules = computed(() => rules.value.length)
const activeRules = computed(() => rules.value.filter(r => r.status === 'active').length)
const triggeredCount = computed(() => rules.value.reduce((sum, r) => sum + r.triggerCount, 0))
const accuracy = computed(() => 94)

const filteredRules = computed(() => {
  let result = [...rules.value]
  if (activeTab.value !== 'all') {
    result = result.filter(r => r.type === activeTab.value)
  }
  if (filters.value.severity !== 'all') {
    result = result.filter(r => r.severity === filters.value.severity)
  }
  if (filters.value.status !== 'all') {
    result = result.filter(r => r.status === filters.value.status)
  }
  if (filters.value.category !== 'all') {
    result = result.filter(r => r.category === filters.value.category)
  }
  if (filters.value.search) {
    const search = filters.value.search.toLowerCase()
    result = result.filter(r =>
        r.name.toLowerCase().includes(search) ||
        r.condition.toLowerCase().includes(search) ||
        r.action.toLowerCase().includes(search)
    )
  }
  return result
})

const paginatedRules = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredRules.value.slice(start, end)
})

// Helper Functions
const getRuleTypeLabel = (type: string) => {
  const map: Record<string, string> = {
    threshold: 'Threshold',
    status: 'Status',
    temporal: 'Temporal',
    composite: 'Composite'
  }
  return map[type] || type
}

const getRuleTypeTag = (type: string) => {
  const map: Record<string, string> = {
    threshold: 'primary',
    status: 'success',
    temporal: 'warning',
    composite: 'danger'
  }
  return map[type] || 'info'
}

const getSeverityTag = (severity: string) => {
  const map: Record<string, string> = {
    critical: 'danger',
    major: 'warning',
    minor: 'info'
  }
  return map[severity] || 'info'
}

const ruleForm = ref({
  name: '',
  type: 'threshold' as 'threshold' | 'status' | 'temporal' | 'composite',
  condition: '',
  action: '',
  severity: 'major' as 'critical' | 'major' | 'minor',
  category: 'HVAC',
  priority: 5
})

// 初始化图表
const initStatsChart = () => {
  if (!statsChartRef.value) {
    console.warn('statsChartRef is not ready')
    return
  }

  if (statsChart) {
    statsChart.dispose()
  }

  statsChart = echarts.init(statsChartRef.value)
  const data = chartDataMap[statsPeriod.value as keyof typeof chartDataMap]

  statsChart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        let result = `${params[0].axisValue}<br/>`
        params.forEach((p: any) => {
          result += `${p.marker} ${p.seriesName}: ${p.value} times<br/>`
        })
        return result
      }
    },
    legend: {
      data: ['Rules Triggered', 'Faults Resolved'],
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      top: '10%',
      bottom: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: data.xAxis,
      axisLabel: {
        rotate: statsPeriod.value === 'day' ? 45 : 0,
        interval: 0
      }
    },
    yAxis: {
      type: 'value',
      name: 'Count',
      axisLabel: {
        formatter: '{value}'
      }
    },
    series: [
      {
        name: 'Rules Triggered',
        type: 'line',
        data: data.triggered,
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: { width: 3, color: '#f56c6c' },
        areaStyle: { opacity: 0.1, color: '#f56c6c' },
        itemStyle: { color: '#f56c6c' }
      },
      {
        name: 'Faults Resolved',
        type: 'line',
        data: data.resolved,
        smooth: true,
        symbol: 'diamond',
        symbolSize: 8,
        lineStyle: { width: 2, color: '#67c23a' },
        areaStyle: { opacity: 0.1, color: '#67c23a' },
        itemStyle: { color: '#67c23a' }
      }
    ]
  })
}

// 图表数据更新
const updateChartData = () => {
  if (!statsChart) return
  const data = chartDataMap[statsPeriod.value as keyof typeof chartDataMap]
  statsChart.setOption({
    xAxis: { data: data.xAxis },
    series: [
      { data: data.triggered },
      { data: data.resolved }
    ]
  })
}

// Period change handler
const onStatsPeriodChange = () => {
  updateChartData()
}

// 窗口大小变化时重新调整图表
const handleResize = () => {
  if (statsChart) {
    statsChart.resize()
  }
}

// Actions
const refreshData = () => {
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
    ElMessage.success('Rules refreshed')
  }, 500)
}

const openCreateRuleDialog = () => {
  editingRule.value = null
  ruleForm.value = {
    name: '',
    type: 'threshold',
    condition: '',
    action: '',
    severity: 'major',
    category: 'HVAC',
    priority: 5
  }
  ruleDialogVisible.value = true
}

const editRule = (rule: Rule) => {
  editingRule.value = rule
  ruleForm.value = {
    name: rule.name,
    type: rule.type,
    condition: rule.condition,
    action: rule.action,
    severity: rule.severity,
    category: rule.category,
    priority: rule.priority
  }
  ruleDialogVisible.value = true
}

const saveRule = () => {
  if (!ruleForm.value.name || !ruleForm.value.condition || !ruleForm.value.action) {
    ElMessage.warning('Please fill all required fields')
    return
  }

  if (editingRule.value) {
    const index = rules.value.findIndex(r => r.id === editingRule.value!.id)
    if (index !== -1) {
      rules.value[index] = {
        ...rules.value[index],
        name: ruleForm.value.name,
        type: ruleForm.value.type,
        condition: ruleForm.value.condition,
        action: ruleForm.value.action,
        severity: ruleForm.value.severity,
        category: ruleForm.value.category,
        priority: ruleForm.value.priority
      }
      ElMessage.success('Rule updated')
    }
  } else {
    const newId = Math.max(...rules.value.map(r => r.id), 0) + 1
    rules.value.push({
      id: newId,
      name: ruleForm.value.name,
      type: ruleForm.value.type,
      condition: ruleForm.value.condition,
      action: ruleForm.value.action,
      severity: ruleForm.value.severity,
      category: ruleForm.value.category,
      status: 'active',
      priority: ruleForm.value.priority,
      triggerCount: 0,
      createdAt: new Date().toISOString().slice(0, 10)
    })
    ElMessage.success('Rule created')
  }
  ruleDialogVisible.value = false
}

const deleteRule = (rule: Rule) => {
  ElMessageBox.confirm(`Delete rule "${rule.name}"?`, 'Confirm', { type: 'warning' })
      .then(() => {
        const index = rules.value.findIndex(r => r.id === rule.id)
        if (index !== -1) {
          rules.value.splice(index, 1)
          ElMessage.success('Rule deleted')
        }
      })
      .catch(() => {})
}

const toggleRuleStatus = (rule: Rule) => {
  ElMessage.success(`Rule "${rule.name}" ${rule.status === 'active' ? 'activated' : 'deactivated'}`)
}

const openTestDialog = (rule: Rule) => {
  selectedTestRule.value = rule
  testInputData.value = ''
  testResultData.value = null
  testDialogVisible.value = true
}

const executeTest = () => {
  if (!selectedTestRule.value) return
  setTimeout(() => {
    const hasInput = testInputData.value.length > 0
    testResultData.value = {
      matched: hasInput,
      action: hasInput ? selectedTestRule.value?.action : null
    }
  }, 500)
}

const testAllRules = () => {
  ElMessage.info('Testing all rules against current system state...')
  setTimeout(() => {
    ElMessage.success('All rules tested - 8 rules matched current state')
  }, 2000)
}

const handleTabChange = () => {
  currentPage.value = 1
}

const handleSizeChange = () => { currentPage.value = 1 }
const handleCurrentChange = () => {}

// Lifecycle
onMounted(() => {
  let idx = 0
  const msgInterval = setInterval(() => {
    if (idx < loadingMessages.length - 1) {
      idx++
      loadingMessage.value = loadingMessages[idx]
    }
  }, 400)
  const progInterval = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 15 + 5
      if (loadingProgress.value > 100) loadingProgress.value = 100
    }
  }, 200)
  setTimeout(() => {
    clearInterval(msgInterval)
    clearInterval(progInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(() => {
      isLoaded.value = true
      nextTick(() => {
        initStatsChart()
      })
      window.addEventListener('resize', handleResize)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (statsChart) {
    statsChart.dispose()
    statsChart = null
  }
})
</script>

<style scoped>
/* 保持原有样式，添加图表容器样式 */
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
.loading-dots { display: inline-flex; gap: 2px; }
.loading-dots span { animation: bounce 1.4s infinite ease-in-out both; }
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

/* Main Content */
.fault-rules-engine-page {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}
.title-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  color: white;
  margin-bottom: 12px;
}
.header-title h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 8px 0;
}
.header-title .subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}
.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}
.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #e2e8f0;
  background: white;
  color: #475569;
}
.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
.action-btn.primary {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  border: none;
  color: white;
}
.action-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3);
}

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}
.kpi-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}
.kpi-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}
.kpi-icon.total { background: #e8f4ff; color: #3b82f6; }
.kpi-icon.active { background: #d1fae5; color: #059669; }
.kpi-icon.triggered { background: #fee2e2; color: #dc2626; }
.kpi-icon.accuracy { background: #fef3c7; color: #d97706; }
.kpi-info { flex: 1; }
.kpi-value { font-size: 28px; font-weight: 700; color: #1a1a2e; }
.kpi-label { font-size: 13px; color: #64748b; margin-top: 4px; }

/* Tabs Card */
.tabs-card {
  background: white;
  border-radius: 16px;
  padding: 0 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

/* Filters Bar */
.filters-bar {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 20px;
  padding: 16px 20px;
  background: white;
  border-radius: 16px;
  align-items: flex-end;
}
.filter-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.filter-group label {
  font-size: 12px;
  font-weight: 500;
  color: #64748b;
}
.filter-select, .search-input {
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 13px;
  background: white;
  min-width: 130px;
}
.search-input { width: 200px; }

/* Table Card */
.table-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}
.pagination-wrapper {
  padding-top: 16px;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #e2e8f0;
  margin-top: 16px;
}

/* Stats Card */
.stats-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}
.card-header h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  color: #1a1a2e;
}
.stats-chart-wrapper {
  width: 100%;
  min-height: 360px;
}
.stats-chart {
  width: 100%;
  height: 360px;
}

/* Test Dialog */
.test-content {
  padding: 8px 0;
}
.test-rule-name {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e2e8f0;
}
.test-condition {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 16px;
}
.test-input label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #475569;
  margin-bottom: 8px;
}
.test-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 12px;
  font-family: monospace;
  resize: vertical;
}
.test-result {
  margin-top: 16px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 12px;
}
.result-title {
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 8px;
}
.result-status {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
}
.result-status.matched { color: #10b981; }
.result-status.not-matched { color: #ef4444; }
.result-action {
  font-size: 13px;
  color: #475569;
}

:deep(.el-table) { border-radius: 12px; }
:deep(.el-table th) { background-color: #fafafa; font-weight: 600; }
:deep(.el-radio-group) { margin-bottom: 0; }
</style>