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
        <div class="loading-tip">Escalation Rules</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="escalation-dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div class="header-left">
        <h1 class="dashboard-title">
          <el-icon><Top /></el-icon>
          Escalation Rules
        </h1>
        <div class="header-stats">
          <div class="stat-badge">
            <el-icon><Grid /></el-icon>
            {{ totalRules }} Active Rules
          </div>
          <div class="stat-badge">
            <el-icon><Bell /></el-icon>
            {{ totalEscalations }} Escalations (24h)
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
        <div class="stat-icon" style="background: #fef0f0; color: #f56c6c;">⏰</div>
        <div class="stat-info">
          <div class="stat-value">{{ criticalRules }}</div>
          <div class="stat-label">Critical Rules</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #fdf6ec; color: #e6a23c;">📈</div>
        <div class="stat-info">
          <div class="stat-value">{{ majorRules }}</div>
          <div class="stat-label">Major Rules</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #fdf6ec; color: #fbbf24;">🔄</div>
        <div class="stat-info">
          <div class="stat-value">{{ warningRules }}</div>
          <div class="stat-label">Warning Rules</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #ecf5ff; color: #409eff;">📋</div>
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
        <el-select v-model="escalationLevelFilter" placeholder="Escalation Level" size="default" style="width: 150px" clearable>
          <el-option label="All Levels" value="all" />
          <el-option label="Level 1" value="1" />
          <el-option label="Level 2" value="2" />
          <el-option label="Level 3" value="3" />
        </el-select>
      </div>
    </div>

    <!-- Escalation Matrix -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">
          <el-icon><DataLine /></el-icon>
          Escalation Matrix
        </div>
        <div class="card-actions">
          <el-button size="small" @click="viewEscalationMatrix">
            <el-icon><View /></el-icon>
            View Full Matrix
          </el-button>
        </div>
      </div>
      <div class="escalation-matrix">
        <el-table :data="escalationMatrix" border stripe size="small">
          <el-table-column prop="severity" label="Severity"  fixed align="center" />
          <el-table-column prop="level1" label="Level 1 (5 min)"  align="center"/>
          <el-table-column prop="level2" label="Level 2 (15 min)" align="center"/>
          <el-table-column prop="level3" label="Level 3 (30 min)" align="center" />
          <el-table-column prop="level4" label="Level 4 (60 min)" align="center"/>
        </el-table>
      </div>
    </div>

    <!-- Rules Table -->
    <div class="card table-card">
      <div class="card-header">
        <div class="card-title">
          <el-icon><List /></el-icon>
          Escalation Rules List
        </div>
        <div class="table-info">
          Showing {{ paginatedRules.length }} of {{ filteredRules.length }} rules
        </div>
      </div>
      <el-table :data="paginatedRules" stripe border style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="name" label="Rule Name" min-width="180" />
        <el-table-column prop="triggerCondition" label="Trigger Condition" min-width="200">
          <template #default="{ row }">
            <div class="trigger-condition">{{ row.triggerCondition }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="severity" label="Severity" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityTag(row.severity)" size="small">
              {{ row.severity.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="escalationLevels" label="Escalation Path" min-width="250">
          <template #default="{ row }">
            <div class="escalation-path">
              <div v-for="(level, idx) in row.escalationLevels" :key="idx" class="path-step">
                <span class="step-time">{{ level.time }}</span>
                <span class="step-arrow">→</span>
                <span class="step-target">{{ level.target }}</span>
                <span class="step-method">{{ level.method }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-switch v-model="row.status" active-value="active" inactive-value="inactive" @change="toggleRuleStatus(row)" />
          </template>
        </el-table-column>
        <el-table-column prop="triggerCount" label="Triggers (24h)" width="110" sortable />
        <el-table-column prop="lastTriggered" label="Last Triggered" width="160" sortable />
        <el-table-column label="Actions" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="editRule(row)">
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-button type="danger" link size="small" @click="deleteRule(row)">
              <el-icon><Delete /></el-icon>
            </el-button>
            <el-dropdown @command="(cmd) => handleEscalationAction(cmd, row)" trigger="click">
              <el-button type="info" link size="small">
                More <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="view">View History</el-dropdown-item>
                  <el-dropdown-item command="test">Test Rule</el-dropdown-item>
                  <el-dropdown-item command="override">Override Now</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
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

    <!-- Recent Escalations -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">
          <el-icon><Timer /></el-icon>
          Recent Escalations
        </div>
      </div>
      <div class="recent-escalations">
        <div v-for="esc in recentEscalations" :key="esc.id" class="escalation-item">
          <div class="escalation-icon" :class="esc.severity">
            <el-icon><Top /></el-icon>
          </div>
          <div class="escalation-details">
            <div class="escalation-title">
              <el-tag :type="getSeverityTag(esc.severity)" size="small">{{ esc.severity.toUpperCase() }}</el-tag>
              <span>{{ esc.ruleName }}</span>
            </div>
            <div class="escalation-info">
              <span><el-icon><Location /></el-icon> {{ esc.alarmTitle }}</span>
              <span><el-icon><User /></el-icon> Escalated to {{ esc.escalatedTo }}</span>
              <span><el-icon><Clock /></el-icon> {{ esc.time }}</span>
            </div>
            <div class="escalation-status" :class="esc.status">
              {{ esc.status === 'pending' ? '⏳ Pending' : (esc.status === 'acknowledged' ? '✅ Acknowledged' : '✅ Resolved') }}
            </div>
          </div>
        </div>
        <div v-if="recentEscalations.length === 0" class="empty-state">
          <el-empty description="No recent escalations" :image-size="60" />
        </div>
      </div>
    </div>

    <!-- Create/Edit Rule Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="650px">
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="130px">
        <el-form-item label="Rule Name" prop="name">
          <el-input v-model="formData.name" placeholder="Enter rule name" />
        </el-form-item>

        <el-form-item label="Trigger Condition" prop="triggerCondition">
          <el-select v-model="formData.triggerCondition" placeholder="Select trigger condition" style="width: 100%">
            <el-option label="Alarm not acknowledged after time" value="timeout" />
            <el-option label="Alarm severity escalation" value="severity_increase" />
            <el-option label="Repeat alarm count" value="repeat_count" />
            <el-option label="Alarm duration threshold" value="duration" />
          </el-select>
        </el-form-item>

        <el-form-item label="Condition Details" prop="conditionValue">
          <div class="condition-details">
            <template v-if="formData.triggerCondition === 'timeout'">
              <el-input-number v-model="formData.timeoutMinutes" :min="1" :max="1440" :step="5" style="width: 150px" />
              <span class="form-tip">minutes without acknowledgment</span>
            </template>
            <template v-else-if="formData.triggerCondition === 'severity_increase'">
              <el-select v-model="formData.fromSeverity" placeholder="From" style="width: 100px">
                <el-option label="Warning" value="warning" />
                <el-option label="Major" value="major" />
              </el-select>
              <span>→</span>
              <el-select v-model="formData.toSeverity" placeholder="To" style="width: 100px">
                <el-option label="Major" value="major" />
                <el-option label="Critical" value="critical" />
              </el-select>
            </template>
            <template v-else-if="formData.triggerCondition === 'repeat_count'">
              <el-input-number v-model="formData.repeatCount" :min="2" :max="50" :step="1" style="width: 120px" />
              <span class="form-tip">occurrences within</span>
              <el-input-number v-model="formData.repeatWindow" :min="1" :max="60" :step="1" style="width: 100px" />
              <span class="form-tip">minutes</span>
            </template>
            <template v-else-if="formData.triggerCondition === 'duration'">
              <el-input-number v-model="formData.durationMinutes" :min="5" :max="720" :step="10" style="width: 120px" />
              <span class="form-tip">minutes active</span>
            </template>
          </div>
        </el-form-item>

        <el-form-item label="Severity" prop="severity">
          <el-select v-model="formData.severity" placeholder="Select severity" style="width: 100%">
            <el-option label="Critical" value="critical" />
            <el-option label="Major" value="major" />
            <el-option label="Warning" value="warning" />
            <el-option label="Info" value="info" />
          </el-select>
        </el-form-item>

        <el-form-item label="Escalation Levels" prop="escalationLevels" required>
          <div class="escalation-levels-editor">
            <div v-for="(level, idx) in formData.escalationLevels" :key="idx" class="escalation-level-row">
              <div class="level-header">
                <span class="level-title">Level {{ idx + 1 }}</span>
                <el-button type="danger" link size="small" @click="removeEscalationLevel(idx)" v-if="formData.escalationLevels.length > 1">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
              <div class="level-fields">
                <el-input-number v-model="level.time" :min="1" :max="120" :step="5" style="width: 100px" placeholder="Time" />
                <span class="form-tip">minutes</span>
                <el-select v-model="level.target" placeholder="Escalate to" style="width: 150px">
                  <el-option label="Level 1 Support" value="Level 1 Support" />
                  <el-option label="Level 2 Support" value="Level 2 Support" />
                  <el-option label="Level 3 Support" value="Level 3 Support" />
                  <el-option label="On-Call Engineer" value="On-Call Engineer" />
                  <el-option label="Duty Manager" value="Duty Manager" />
                  <el-option label="IT Director" value="IT Director" />
                </el-select>
                <el-select v-model="level.method" placeholder="Notification Method" style="width: 120px">
                  <el-option label="Email" value="Email" />
                  <el-option label="SMS" value="SMS" />
                  <el-option label="Email + SMS" value="Both" />
                  <el-option label="Phone Call" value="Phone" />
                </el-select>
              </div>
            </div>
            <el-button type="primary" link @click="addEscalationLevel" style="margin-top: 12px">
              <el-icon><Plus /></el-icon>
              Add Escalation Level
            </el-button>
          </div>
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
    <el-dialog v-model="detailDialogVisible" :title="`Rule Details - ${selectedRule?.name}`" width="650px">
      <el-descriptions :column="2" border v-if="selectedRule">
        <el-descriptions-item label="Rule Name">{{ selectedRule.name }}</el-descriptions-item>
        <el-descriptions-item label="Trigger Condition">{{ getTriggerConditionText(selectedRule.triggerCondition) }}</el-descriptions-item>
        <el-descriptions-item label="Condition Details" :span="2">{{ selectedRule.conditionDetail }}</el-descriptions-item>
        <el-descriptions-item label="Severity">
          <el-tag :type="getSeverityTag(selectedRule.severity)">{{ selectedRule.severity.toUpperCase() }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="selectedRule.status === 'active' ? 'success' : 'info'">{{ selectedRule.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Escalation Path" :span="2">
          <div class="detail-escalation-path">
            <div v-for="(level, idx) in selectedRule.escalationLevels" :key="idx" class="detail-step">
              <span class="step-number">Level {{ idx + 1 }}</span>
              <span class="step-time">{{ level.time }} min</span>
              <span class="step-arrow">→</span>
              <span class="step-target">{{ level.target }}</span>
              <span class="step-method">({{ level.method }})</span>
            </div>
          </div>
        </el-descriptions-item>
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
import { Top, Grid, Bell, Plus, Refresh, Search, Edit, Delete, List, DataLine, View, Timer, Location, User, Clock, ArrowDown } from '@element-plus/icons-vue'
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
  'Loading escalation rules...',
  'Building escalation matrix...',
  'Initializing dashboard...',
  'Almost ready...'
]

// ==================== Data State ====================
const searchText = ref('')
const severityFilter = ref('all')
const statusFilter = ref('all')
const escalationLevelFilter = ref('all')
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const dialogTitle = ref('Create Rule')
const formRef = ref()
const selectedRule = ref<any>(null)

const pagination = ref({ page: 1, pageSize: 10 })

// Escalation Rule Interface
interface EscalationLevel {
  time: number
  target: string
  method: string
}

interface EscalationRule {
  id: number
  name: string
  triggerCondition: string
  conditionDetail: string
  severity: string
  status: 'active' | 'inactive'
  escalationLevels: EscalationLevel[]
  description: string
  triggerCount: number
  lastTriggered: string
  createdAt: string
}

const rules = ref<EscalationRule[]>([])

// Escalation Matrix
const escalationMatrix = ref([
  { severity: 'Critical', level1: 'Level 2 Support', level2: 'On-Call Engineer', level3: 'IT Manager', level4: 'CTO' },
  { severity: 'Major', level1: 'Level 1 Support', level2: 'Level 2 Support', level3: 'On-Call Engineer', level4: 'IT Manager' },
  { severity: 'Warning', level1: 'Level 1 Support', level2: 'Level 2 Support', level3: 'Email Notification', level4: '-' },
  { severity: 'Info', level1: 'Email Only', level2: '-', level3: '-', level4: '-' }
])

// Recent Escalations
const recentEscalations = ref([
  { id: 1, severity: 'critical', ruleName: 'Critical Alarm Escalation', alarmTitle: 'UPS Overload Detected', escalatedTo: 'On-Call Engineer', time: '5 min ago', status: 'pending' },
  { id: 2, severity: 'major', ruleName: 'Major Alarm Escalation', alarmTitle: 'High CPU Usage', escalatedTo: 'Level 2 Support', time: '12 min ago', status: 'acknowledged' },
  { id: 3, severity: 'warning', ruleName: 'Warning Escalation', alarmTitle: 'Temperature High', escalatedTo: 'Level 1 Support', time: '25 min ago', status: 'resolved' },
  { id: 4, severity: 'critical', ruleName: 'Unacknowledged Alarm', alarmTitle: 'Network Core Down', escalatedTo: 'IT Director', time: '45 min ago', status: 'pending' },
  { id: 5, severity: 'major', ruleName: 'Repeat Alarm Escalation', alarmTitle: 'Disk Space Warning', escalatedTo: 'Level 2 Support', time: '1 hour ago', status: 'acknowledged' }
])

// Generate mock rules
const generateRules = (): EscalationRule[] => {
  return [
    { id: 1, name: 'Critical Alarm Escalation', triggerCondition: 'timeout', conditionDetail: 'Not acknowledged within 5 minutes', severity: 'critical', status: 'active', escalationLevels: [{ time: 5, target: 'Level 2 Support', method: 'Email + SMS' }, { time: 15, target: 'On-Call Engineer', method: 'Phone Call' }, { time: 30, target: 'IT Manager', method: 'Phone + SMS' }], description: 'Escalate critical alarms to higher levels if not acknowledged', triggerCount: 12, lastTriggered: '2024-06-03 14:30:22', createdAt: '2024-01-10' },
    { id: 2, name: 'Major Alarm Escalation', triggerCondition: 'timeout', conditionDetail: 'Not acknowledged within 10 minutes', severity: 'major', status: 'active', escalationLevels: [{ time: 10, target: 'Level 2 Support', method: 'Email' }, { time: 25, target: 'On-Call Engineer', method: 'Email + SMS' }], description: 'Escalate major alarms if not acknowledged', triggerCount: 8, lastTriggered: '2024-06-03 13:20:45', createdAt: '2024-01-10' },
    { id: 3, name: 'Severity Escalation Rule', triggerCondition: 'severity_increase', conditionDetail: 'Warning → Major after 3 occurrences', severity: 'warning', status: 'active', escalationLevels: [{ time: 0, target: 'Level 2 Support', method: 'Email' }], description: 'Escalate severity when alarm repeats', triggerCount: 5, lastTriggered: '2024-06-03 10:15:30', createdAt: '2024-01-15' },
    { id: 4, name: 'Repeat Alarm Escalation', triggerCondition: 'repeat_count', conditionDetail: '5 times within 30 minutes', severity: 'major', status: 'active', escalationLevels: [{ time: 0, target: 'Level 2 Support', method: 'Email + SMS' }, { time: 10, target: 'On-Call Engineer', method: 'Phone Call' }], description: 'Escalate when same alarm repeats frequently', triggerCount: 4, lastTriggered: '2024-06-03 09:45:12', createdAt: '2024-01-20' },
    { id: 5, name: 'Long Duration Alarm', triggerCondition: 'duration', conditionDetail: 'Active for 60 minutes', severity: 'warning', status: 'active', escalationLevels: [{ time: 30, target: 'Level 2 Support', method: 'Email' }], description: 'Escalate when alarm persists', triggerCount: 2, lastTriggered: '2024-06-02 16:20:00', createdAt: '2024-02-01' }
  ]
}

// Statistics
const totalRules = computed(() => rules.value.length)
const totalEscalations = computed(() => rules.value.reduce((sum, r) => sum + r.triggerCount, 0))
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

  if (escalationLevelFilter.value !== 'all') {
    // Filter based on number of escalation levels
    const level = parseInt(escalationLevelFilter.value)
    filtered = filtered.filter(r => r.escalationLevels.length >= level)
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
  triggerCondition: 'timeout',
  timeoutMinutes: 5,
  fromSeverity: 'warning',
  toSeverity: 'major',
  repeatCount: 5,
  repeatWindow: 30,
  durationMinutes: 60,
  severity: 'warning',
  escalationLevels: [
    { time: 5, target: 'Level 1 Support', method: 'Email' },
    { time: 15, target: 'Level 2 Support', method: 'Email + SMS' }
  ],
  description: ''
})

const formRules = {
  name: [{ required: true, message: 'Please enter rule name', trigger: 'blur' }],
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

const getTriggerConditionText = (condition: string) => {
  const map: Record<string, string> = {
    timeout: 'Time-based Escalation',
    severity_increase: 'Severity Escalation',
    repeat_count: 'Repeat Count Escalation',
    duration: 'Duration-based Escalation'
  }
  return map[condition] || condition
}

// ==================== Actions ====================
const toggleRuleStatus = (rule: EscalationRule) => {
  const statusText = rule.status === 'active' ? 'activated' : 'deactivated'
  ElMessage.success(`Rule "${rule.name}" ${statusText}`)
}

const addEscalationLevel = () => {
  const lastLevel = formData.value.escalationLevels[formData.value.escalationLevels.length - 1]
  const newTime = (lastLevel?.time || 5) + 10
  formData.value.escalationLevels.push({
    time: newTime,
    target: 'Level 2 Support',
    method: 'Email'
  })
}

const removeEscalationLevel = (index: number) => {
  formData.value.escalationLevels.splice(index, 1)
}

const handleCreateRule = () => {
  dialogTitle.value = 'Create Rule'
  formData.value = {
    name: '',
    triggerCondition: 'timeout',
    timeoutMinutes: 5,
    fromSeverity: 'warning',
    toSeverity: 'major',
    repeatCount: 5,
    repeatWindow: 30,
    durationMinutes: 60,
    severity: 'warning',
    escalationLevels: [
      { time: 5, target: 'Level 1 Support', method: 'Email' },
      { time: 15, target: 'Level 2 Support', method: 'Email + SMS' }
    ],
    description: ''
  }
  dialogVisible.value = true
}

const editRule = (rule: EscalationRule) => {
  dialogTitle.value = 'Edit Rule'
  formData.value = {
    name: rule.name,
    triggerCondition: rule.triggerCondition,
    timeoutMinutes: 5,
    fromSeverity: 'warning',
    toSeverity: 'major',
    repeatCount: 5,
    repeatWindow: 30,
    durationMinutes: 60,
    severity: rule.severity,
    escalationLevels: [...rule.escalationLevels],
    description: rule.description
  }
  dialogVisible.value = true
}

const deleteRule = (rule: EscalationRule) => {
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

const handleEscalationAction = (command: string, rule: EscalationRule) => {
  if (command === 'view') {
    selectedRule.value = rule
    detailDialogVisible.value = true
  } else if (command === 'test') {
    ElMessage.info(`Testing rule "${rule.name}"...`)
    setTimeout(() => {
      ElMessage.success(`Rule "${rule.name}" test completed. Escalation would trigger.`)
    }, 1000)
  } else if (command === 'override') {
    ElMessageBox.confirm(`Override escalation for rule "${rule.name}"? This will trigger escalation immediately.`, 'Confirm', {
      confirmButtonText: 'Override',
      cancelButtonText: 'Cancel',
      type: 'warning'
    }).then(() => {
      ElMessage.success(`Escalation overridden for "${rule.name}"`)
    }).catch(() => {})
  }
}

const viewEscalationMatrix = () => {
  ElMessage.info('Full escalation matrix view')
}

const submitForm = async () => {
  try {
    await formRef.value?.validate()
    if (formData.value.escalationLevels.length === 0) {
      ElMessage.warning('Please add at least one escalation level')
      return
    }
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
.escalation-dashboard {
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

.stat-value .unit {
  font-size: 12px;
  font-weight: normal;
  color: #909399;
  margin-left: 2px;
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

.card-actions {
  display: flex;
  gap: 8px;
}

/* Table */
.table-card {
  overflow-x: auto;
}

.card-footer {
  padding: 16px 20px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  justify-content: flex-end;
  background: #fafafa;
}

.table-info {
  font-size: 13px;
  color: #909399;
}

/* Escalation Matrix */
.escalation-matrix {
  padding: 16px;
}

/* Escalation Path */
.escalation-path {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.path-step {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 11px;
}

.step-time {
  color: #409eff;
  font-weight: 500;
}

.step-arrow {
  color: #909399;
}

.step-target {
  color: #1f2f3d;
}

.step-method {
  color: #67c23a;
  font-size: 10px;
}

.trigger-condition {
  font-size: 12px;
  color: #606266;
  font-family: monospace;
}

/* Recent Escalations */
.recent-escalations {
  padding: 8px;
  max-height: 300px;
  overflow-y: auto;
}

.escalation-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid #e4e7ed;
  transition: background 0.2s;
}

.escalation-item:hover {
  background: #f5f7fa;
}

.escalation-icon {
  width: 40px;
  height: 40px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fef0f0;
  color: #f56c6c;
}

.escalation-icon.critical { background: #fef0f0; color: #f56c6c; }
.escalation-icon.major { background: #fdf6ec; color: #e6a23c; }
.escalation-icon.warning { background: #fdf6ec; color: #fbbf24; }

.escalation-details {
  flex: 1;
}

.escalation-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  font-weight: 500;
  color: #1f2f3d;
}

.escalation-info {
  display: flex;
  gap: 16px;
  font-size: 11px;
  color: #909399;
  margin-bottom: 6px;
}

.escalation-info span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.escalation-status {
  font-size: 11px;
  font-weight: 500;
}

.escalation-status.pending { color: #e6a23c; }
.escalation-status.acknowledged { color: #409eff; }
.escalation-status.resolved { color: #67c23a; }

.empty-state {
  padding: 20px;
  text-align: center;
}

/* Escalation Levels Editor */
.escalation-levels-editor {
  width: 100%;
}

.escalation-level-row {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;
}

.level-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.level-title {
  font-weight: 500;
  color: #409eff;
}

.level-fields {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.condition-details {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.form-tip {
  font-size: 12px;
  color: #909399;
}

.detail-escalation-path {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-step {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  border-bottom: 1px solid #e4e7ed;
}

.step-number {
  font-weight: 600;
  color: #409eff;
  width: 60px;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .escalation-dashboard {
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
  .level-fields {
    flex-direction: column;
    align-items: stretch;
  }
  .escalation-info {
    flex-direction: column;
    gap: 4px;
  }
  .escalation-path {
    flex-direction: column;
    align-items: flex-start;
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