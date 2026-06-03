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
          <span class="loading-title">Loading</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Threshold Rules</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="threshold-rules-dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div class="header-left">
        <h1 class="dashboard-title">
          <el-icon><Setting /></el-icon>
          Threshold Rules
        </h1>
        <div class="header-stats">
          <div class="stat-badge">
            <el-icon><Grid /></el-icon>
            {{ totalRules }} Active Rules
          </div>
          <div class="stat-badge">
            <el-icon><Bell /></el-icon>
            {{ totalTriggers }} Triggers (24h)
          </div>
        </div>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="handleCreateRule">
          <el-icon><Plus /></el-icon>
          Create Rule
        </el-button>
        <el-button @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon" style="background: #fef0f0; color: #f56c6c;">⚠️</div>
        <div class="stat-info">
          <div class="stat-value">{{ criticalRules }}</div>
          <div class="stat-label">Critical Rules</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #fdf6ec; color: #e6a23c;">🟠</div>
        <div class="stat-info">
          <div class="stat-value">{{ majorRules }}</div>
          <div class="stat-label">Major Rules</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #fdf6ec; color: #fbbf24;">🟡</div>
        <div class="stat-info">
          <div class="stat-value">{{ warningRules }}</div>
          <div class="stat-label">Warning Rules</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #ecf5ff; color: #409eff;">🔵</div>
        <div class="stat-info">
          <div class="stat-value">{{ infoRules }}</div>
          <div class="stat-label">Info Rules</div>
        </div>
      </div>
    </div>

    <!-- Search & Filter Bar -->
    <div class="filter-bar">
      <div class="filter-group">
        <el-input v-model="searchText" placeholder="Search rules..." size="default" style="width: 250px" clearable>
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-select v-model="severityFilter" placeholder="Severity" size="default" style="width: 130px" clearable>
          <el-option label="All" value="all" />
          <el-option label="Critical" value="critical" />
          <el-option label="Major" value="major" />
          <el-option label="Warning" value="warning" />
          <el-option label="Info" value="info" />
        </el-select>
        <el-select v-model="statusFilter" placeholder="Status" size="default" style="width: 130px" clearable>
          <el-option label="All" value="all" />
          <el-option label="Active" value="active" />
          <el-option label="Inactive" value="inactive" />
        </el-select>
        <el-select v-model="metricFilter" placeholder="Metric Type" size="default" style="width: 150px" clearable>
          <el-option label="All Metrics" value="all" />
          <el-option label="Temperature" value="Temperature" />
          <el-option label="Humidity" value="Humidity" />
          <el-option label="CPU Usage" value="CPU" />
          <el-option label="Memory" value="Memory" />
          <el-option label="Power" value="Power" />
          <el-option label="Network" value="Network" />
        </el-select>
      </div>
    </div>

    <!-- Rules Table -->
    <div class="card table-card">
      <div class="card-header">
        <div class="card-title">
          <el-icon><List /></el-icon>
          Threshold Rules List
        </div>
        <div class="table-info">
          Showing {{ paginatedRules.length }} of {{ filteredRules.length }} rules
        </div>
      </div>
      <el-table :data="paginatedRules" stripe border style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="name" label="Rule Name" min-width="180" />
        <el-table-column prop="metric" label="Metric" width="120" />
        <el-table-column prop="condition" label="Condition" width="100">
          <template #default="{ row }">
            <el-tag :type="getConditionTag(row.condition)" size="small">{{ row.condition }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="threshold" label="Threshold" width="100" sortable>
          <template #default="{ row }">
            <span class="threshold-value">{{ row.threshold }} {{ row.unit }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="severity" label="Severity" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityTag(row.severity)" size="small">
              {{ row.severity.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-switch v-model="row.status" active-value="active" inactive-value="inactive" @change="toggleRuleStatus(row)" />
          </template>
        </el-table-column>
        <el-table-column prop="triggerCount" label="Triggers (24h)" width="110" sortable />
        <el-table-column prop="lastTriggered" label="Last Triggered" width="160" sortable />
        <el-table-column prop="actions" label="Actions" width="100">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="editRule(row)">
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-button type="danger" link size="small" @click="deleteRule(row)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="card-footer">
        <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="filteredRules.length"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handlePageSizeChange"
            @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- Create/Edit Rule Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="550px">
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="120px">
        <el-form-item label="Rule Name" prop="name">
          <el-input v-model="formData.name" placeholder="Enter rule name" />
        </el-form-item>
        <el-form-item label="Metric" prop="metric">
          <el-select v-model="formData.metric" placeholder="Select metric" style="width: 100%">
            <el-option label="Temperature" value="Temperature" />
            <el-option label="Humidity" value="Humidity" />
            <el-option label="CPU Usage" value="CPU" />
            <el-option label="Memory Usage" value="Memory" />
            <el-option label="Power Consumption" value="Power" />
            <el-option label="Network Bandwidth" value="Network" />
            <el-option label="Disk Usage" value="Disk" />
          </el-select>
        </el-form-item>
        <el-form-item label="Condition" prop="condition">
          <el-select v-model="formData.condition" placeholder="Select condition" style="width: 100%">
            <el-option label="Greater Than (>)" value=">" />
            <el-option label="Greater Than or Equal (>=)" value=">=" />
            <el-option label="Less Than (<)" value="<" />
            <el-option label="Less Than or Equal (<=)" value="<=" />
            <el-option label="Equal (=)" value="=" />
          </el-select>
        </el-form-item>
        <el-form-item label="Threshold" prop="threshold">
          <el-input-number v-model="formData.threshold" :min="0" :max="1000" :step="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Unit" prop="unit">
          <el-input v-model="formData.unit" placeholder="e.g., °C, %, kW" />
        </el-form-item>
        <el-form-item label="Severity" prop="severity">
          <el-select v-model="formData.severity" placeholder="Select severity" style="width: 100%">
            <el-option label="Critical" value="critical" />
            <el-option label="Major" value="major" />
            <el-option label="Warning" value="warning" />
            <el-option label="Info" value="info" />
          </el-select>
        </el-form-item>
        <el-form-item label="Duration (seconds)" prop="duration">
          <el-input-number v-model="formData.duration" :min="0" :max="3600" :step="10" style="width: 100%" />
          <span class="form-tip">Time condition must be met (0 = immediate)</span>
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="formData.description" type="textarea" :rows="2" placeholder="Rule description" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitForm">Save Rule</el-button>
      </template>
    </el-dialog>

    <!-- Rule Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`Rule Details - ${selectedRule?.name}`" width="600px">
      <el-descriptions :column="2" border v-if="selectedRule">
        <el-descriptions-item label="Rule Name">{{ selectedRule.name }}</el-descriptions-item>
        <el-descriptions-item label="Metric">{{ selectedRule.metric }}</el-descriptions-item>
        <el-descriptions-item label="Condition">{{ selectedRule.condition }}</el-descriptions-item>
        <el-descriptions-item label="Threshold">{{ selectedRule.threshold }} {{ selectedRule.unit }}</el-descriptions-item>
        <el-descriptions-item label="Severity">
          <el-tag :type="getSeverityTag(selectedRule.severity)">{{ selectedRule.severity.toUpperCase() }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="selectedRule.status === 'active' ? 'success' : 'info'">{{ selectedRule.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Duration">{{ selectedRule.duration || 0 }} seconds</el-descriptions-item>
        <el-descriptions-item label="Triggers (24h)">{{ selectedRule.triggerCount }}</el-descriptions-item>
        <el-descriptions-item label="Last Triggered">{{ selectedRule.lastTriggered }}</el-descriptions-item>
        <el-descriptions-item label="Created At">{{ selectedRule.createdAt }}</el-descriptions-item>
        <el-descriptions-item label="Description" :span="2">{{ selectedRule.description }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Setting, Grid, Bell, Plus, Refresh, Search, Edit, Delete, List } from '@element-plus/icons-vue'
import { useCounterStore } from '@/stores/counter.js'
import { getCurrentInstance } from 'vue'

const getStore = () => {
  const instance = getCurrentInstance()
  if (!instance) throw new Error('useStore() must be called within a setup function')
  const pinia = instance.appContext.config.globalProperties.$pinia
  if (!pinia) throw new Error('Pinia instance not found')
  return useCounterStore(pinia)
}
const counterStore = getStore()
const isFullscreen = computed(() => counterStore.isFullscreen)
const route = useRoute()

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Preparing...',
  'Loading threshold rules...',
  'Analyzing configurations...',
  'Initializing dashboard...',
  'Almost ready...'
]

// ==================== Data State ====================
const searchText = ref('')
const severityFilter = ref('all')
const statusFilter = ref('all')
const metricFilter = ref('all')
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const dialogTitle = ref('Create Rule')
const formRef = ref()
const selectedRule = ref<any>(null)

const pagination = ref({ page: 1, pageSize: 10 })

// Rule Interface
interface ThresholdRule {
  id: number
  name: string
  metric: string
  condition: string
  threshold: number
  unit: string
  severity: string
  status: 'active' | 'inactive'
  duration: number
  description: string
  triggerCount: number
  lastTriggered: string
  createdAt: string
}

const rules = ref<ThresholdRule[]>([])

// Generate mock rules
const generateRules = (): ThresholdRule[] => {
  return [
    { id: 1, name: 'High Temperature Alert', metric: 'Temperature', condition: '>', threshold: 35, unit: '°C', severity: 'critical', status: 'active', duration: 60, description: 'Trigger when server room temperature exceeds 35°C for 60 seconds', triggerCount: 12, lastTriggered: '2024-06-03 14:30:22', createdAt: '2024-01-10' },
    { id: 2, name: 'Critical Temperature Warning', metric: 'Temperature', condition: '>', threshold: 40, unit: '°C', severity: 'critical', status: 'active', duration: 30, description: 'Emergency alert when temperature reaches 40°C', triggerCount: 3, lastTriggered: '2024-06-02 08:15:30', createdAt: '2024-01-10' },
    { id: 3, name: 'Low Temperature Warning', metric: 'Temperature', condition: '<', threshold: 15, unit: '°C', severity: 'warning', status: 'active', duration: 120, description: 'Alert when temperature drops below 15°C', triggerCount: 0, lastTriggered: 'Never', createdAt: '2024-01-15' },
    { id: 4, name: 'High Humidity Alert', metric: 'Humidity', condition: '>', threshold: 60, unit: '%', severity: 'warning', status: 'active', duration: 60, description: 'Warning when humidity exceeds 60%', triggerCount: 8, lastTriggered: '2024-06-03 10:45:12', createdAt: '2024-01-10' },
    { id: 5, name: 'Low Humidity Alert', metric: 'Humidity', condition: '<', threshold: 30, unit: '%', severity: 'info', status: 'inactive', duration: 60, description: 'Info when humidity drops below 30%', triggerCount: 2, lastTriggered: '2024-05-28 16:20:00', createdAt: '2024-02-01' },
    { id: 6, name: 'High CPU Usage', metric: 'CPU', condition: '>', threshold: 85, unit: '%', severity: 'major', status: 'active', duration: 300, description: 'Alert when CPU usage exceeds 85% for 5 minutes', triggerCount: 25, lastTriggered: '2024-06-03 13:20:45', createdAt: '2024-01-10' },
    { id: 7, name: 'Critical CPU Overload', metric: 'CPU', condition: '>', threshold: 95, unit: '%', severity: 'critical', status: 'active', duration: 60, description: 'Critical alert when CPU exceeds 95%', triggerCount: 5, lastTriggered: '2024-06-02 09:30:00', createdAt: '2024-01-10' },
    { id: 8, name: 'Memory Threshold Exceeded', metric: 'Memory', condition: '>', threshold: 80, unit: '%', severity: 'major', status: 'active', duration: 180, description: 'Alert when memory usage exceeds 80% for 3 minutes', triggerCount: 18, lastTriggered: '2024-06-03 11:15:33', createdAt: '2024-01-10' },
    { id: 9, name: 'Low Memory Warning', metric: 'Memory', condition: '<', threshold: 10, unit: '%', severity: 'info', status: 'inactive', duration: 0, description: 'Info when available memory drops below 10%', triggerCount: 0, lastTriggered: 'Never', createdAt: '2024-02-15' },
    { id: 10, name: 'Power Consumption Spike', metric: 'Power', condition: '>', threshold: 150, unit: 'kW', severity: 'major', status: 'active', duration: 120, description: 'Alert when power consumption exceeds 150kW', triggerCount: 7, lastTriggered: '2024-06-03 09:00:00', createdAt: '2024-01-20' },
    { id: 11, name: 'Critical Power Overload', metric: 'Power', condition: '>', threshold: 200, unit: 'kW', severity: 'critical', status: 'active', duration: 30, description: 'Critical alert for power overload', triggerCount: 2, lastTriggered: '2024-06-01 14:45:00', createdAt: '2024-01-20' },
    { id: 12, name: 'Network Latency High', metric: 'Network', condition: '>', threshold: 100, unit: 'ms', severity: 'warning', status: 'active', duration: 60, description: 'Alert when network latency exceeds 100ms', triggerCount: 15, lastTriggered: '2024-06-03 12:30:22', createdAt: '2024-02-10' },
    { id: 13, name: 'Packet Loss Detected', metric: 'Network', condition: '>', threshold: 5, unit: '%', severity: 'major', status: 'active', duration: 30, description: 'Alert when packet loss exceeds 5%', triggerCount: 4, lastTriggered: '2024-06-02 16:20:15', createdAt: '2024-02-10' },
    { id: 14, name: 'Disk Space Warning', metric: 'Disk', condition: '>', threshold: 85, unit: '%', severity: 'warning', status: 'active', duration: 600, description: 'Warning when disk usage exceeds 85% for 10 minutes', triggerCount: 6, lastTriggered: '2024-06-03 08:00:00', createdAt: '2024-03-01' },
    { id: 15, name: 'Critical Disk Space', metric: 'Disk', condition: '>', threshold: 95, unit: '%', severity: 'critical', status: 'active', duration: 60, description: 'Critical alert for disk space', triggerCount: 1, lastTriggered: '2024-05-30 23:00:00', createdAt: '2024-03-01' }
  ]
}

// Statistics
const totalRules = computed(() => rules.value.length)
const totalTriggers = computed(() => rules.value.reduce((sum, r) => sum + r.triggerCount, 0))
const criticalRules = computed(() => rules.value.filter(r => r.severity === 'critical' && r.status === 'active').length)
const majorRules = computed(() => rules.value.filter(r => r.severity === 'major' && r.status === 'active').length)
const warningRules = computed(() => rules.value.filter(r => r.severity === 'warning' && r.status === 'active').length)
const infoRules = computed(() => rules.value.filter(r => r.severity === 'info' && r.status === 'active').length)

// Filtered rules
const filteredRules = computed(() => {
  let filtered = rules.value

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(r => r.name.toLowerCase().includes(search) || r.description.toLowerCase().includes(search))
  }

  if (severityFilter.value !== 'all') {
    filtered = filtered.filter(r => r.severity === severityFilter.value)
  }

  if (statusFilter.value !== 'all') {
    filtered = filtered.filter(r => r.status === statusFilter.value)
  }

  if (metricFilter.value !== 'all') {
    filtered = filtered.filter(r => r.metric === metricFilter.value)
  }

  return filtered
})

// Paginated rules
const paginatedRules = computed(() => {
  const start = (pagination.value.page - 1) * pagination.value.pageSize
  return filteredRules.value.slice(start, start + pagination.value.pageSize)
})

// Form data
const formData = ref({
  name: '',
  metric: '',
  condition: '>',
  threshold: 50,
  unit: '',
  severity: 'warning',
  duration: 0,
  description: ''
})

const formRules = {
  name: [{ required: true, message: 'Please enter rule name', trigger: 'blur' }],
  metric: [{ required: true, message: 'Please select metric', trigger: 'change' }],
  condition: [{ required: true, message: 'Please select condition', trigger: 'change' }],
  threshold: [{ required: true, message: 'Please enter threshold', trigger: 'blur' }],
  unit: [{ required: true, message: 'Please enter unit', trigger: 'blur' }],
  severity: [{ required: true, message: 'Please select severity', trigger: 'change' }]
}

// Helper functions
const getSeverityTag = (severity: string) => {
  const map: Record<string, string> = {
    critical: 'danger',
    major: 'warning',
    warning: 'warning',
    info: 'info'
  }
  return map[severity] || 'info'
}

const getConditionTag = (condition: string) => {
  const map: Record<string, string> = {
    '>': 'danger',
    '>=': 'danger',
    '<': 'info',
    '<=': 'info',
    '=': 'primary'
  }
  return map[condition] || 'info'
}

// ==================== Actions ====================
const toggleRuleStatus = (rule: ThresholdRule) => {
  const statusText = rule.status === 'active' ? 'activated' : 'deactivated'
  ElMessage.success(`Rule "${rule.name}" ${statusText}`)
}

const handleCreateRule = () => {
  dialogTitle.value = 'Create Rule'
  formData.value = {
    name: '',
    metric: '',
    condition: '>',
    threshold: 50,
    unit: '',
    severity: 'warning',
    duration: 0,
    description: ''
  }
  dialogVisible.value = true
}

const editRule = (rule: ThresholdRule) => {
  dialogTitle.value = 'Edit Rule'
  formData.value = {
    name: rule.name,
    metric: rule.metric,
    condition: rule.condition,
    threshold: rule.threshold,
    unit: rule.unit,
    severity: rule.severity,
    duration: rule.duration,
    description: rule.description
  }
  dialogVisible.value = true
}

const deleteRule = (rule: ThresholdRule) => {
  ElMessageBox.confirm(`Delete rule "${rule.name}"?`, 'Confirm', {
    confirmButtonText: 'Delete',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    const index = rules.value.findIndex(r => r.id === rule.id)
    if (index > -1) {
      rules.value.splice(index, 1)
      ElMessage.success(`Rule "${rule.name}" deleted`)
    }
  }).catch(() => {})
}

const viewDetails = (rule: ThresholdRule) => {
  selectedRule.value = rule
  detailDialogVisible.value = true
}

const submitForm = async () => {
  try {
    await formRef.value?.validate()
    ElMessage.success(dialogTitle.value === 'Create Rule' ? 'Rule created successfully' : 'Rule updated successfully')
    dialogVisible.value = false
  } catch (error) {
    ElMessage.error('Please fill all required fields')
  }
}

const refreshData = async () => {
  refreshing.value = true
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  rules.value = generateRules()
  tableLoading.value = false
  refreshing.value = false
  ElMessage.success('Data refreshed')
}

const handlePageSizeChange = () => {
  pagination.value.page = 1
}

const handlePageChange = () => {}

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
      nextTick(() => {
        setTimeout(() => {
          rules.value = generateRules()
        }, 100)
      })
    }, 500)
  }, 2500)
}

// ==================== Lifecycle ====================
onMounted(() => {
  startLoading()
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

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ==================== Main Dashboard Styles ==================== */
.threshold-rules-dashboard {
  min-height: 100vh;
  background: #ffffff;
  padding: 24px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.dashboard-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
  font-weight: 600;
  color: #1f2f3d;
  margin: 0;
}

.dashboard-title .el-icon {
  color: #409eff;
}

.header-stats {
  display: flex;
  gap: 16px;
  margin-top: 8px;
}

.stat-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px;
  background: #f5f7fa;
  border-radius: 20px;
  font-size: 13px;
  color: #606266;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 14px;
  transition: all 0.3s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #1f2f3d;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

/* Filter Bar */
.filter-bar {
  background: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.filter-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

/* Card */
.card {
  background: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
  flex-wrap: wrap;
  gap: 12px;
  background: #fafafa;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #1f2f3d;
}

.card-title .el-icon {
  color: #409eff;
}

.table-info {
  font-size: 13px;
  color: #909399;
}

.card-footer {
  padding: 16px 20px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  justify-content: flex-end;
  background: #fafafa;
}

.table-card {
  overflow-x: auto;
}

/* Threshold Value */
.threshold-value {
  font-weight: 500;
  color: #409eff;
}

/* Form Tip */
.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  display: block;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .threshold-rules-dashboard {
    padding: 16px;
  }
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .stats-grid {
    grid-template-columns: 1fr;
  }
  .filter-group {
    flex-direction: column;
    width: 100%;
  }
  .filter-group .el-input,
  .filter-group .el-select {
    width: 100% !important;
  }
}

/* Element Plus 样式覆盖 */
:deep(.el-table) {
  background: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: #fafafa;
  --el-table-row-hover-bg-color: #f5f7fa;
  --el-table-border-color: #e4e7ed;
}

:deep(.el-table th.el-table__cell) {
  background-color: #fafafa;
  color: #1f2f3d;
  border-bottom-color: #e4e7ed;
}

:deep(.el-table td.el-table__cell) {
  border-bottom-color: #ebeef5;
  color: #606266;
}

:deep(.el-pagination) {
  --el-pagination-bg-color: transparent;
  --el-pagination-button-bg-color: #f5f7fa;
  --el-pagination-hover-color: #409eff;
}

:deep(.el-dialog) {
  background: #ffffff;
  border-radius: 12px;
}

:deep(.el-dialog__title) {
  color: #1f2f3d;
}
</style>