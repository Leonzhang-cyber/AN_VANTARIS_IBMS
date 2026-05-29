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
        <div class="loading-tip">Rule-Based RCA</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Rule-Based RCA Page Content -->
  <div v-else class="rca-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <div class="title-badge">
          <el-icon><TrendCharts /></el-icon>
          <span>FMS - RCA Engine</span>
        </div>
        <h1>Rule-Based Root Cause Analysis</h1>
        <p class="subtitle">Automated fault diagnosis using predefined rules and inference engine</p>
      </div>
      <div class="header-actions">
        <button class="action-btn" @click="refreshData">
          <el-icon><Refresh /></el-icon>
          <span>Refresh</span>
        </button>
        <button class="action-btn primary" @click="runAnalysis" :loading="analysisRunning">
          <el-icon><TrendCharts /></el-icon>
          <span>{{ analysisRunning ? 'Analyzing...' : 'Run RCA Analysis' }}</span>
        </button>
        <button class="action-btn" @click="openRuleManager">
          <el-icon><Setting /></el-icon>
          <span>Rule Manager</span>
        </button>
      </div>
    </div>

    <!-- KPI Summary Cards -->
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-icon total">
          <el-icon><WarningFilled /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ totalFaults }}</div>
          <div class="kpi-label">Active Faults</div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon analyzed">
          <el-icon><DocumentChecked /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ analyzedCount }}</div>
          <div class="kpi-label">Analyzed</div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon identified">
          <el-icon><Position /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ rootCauseIdentified }}</div>
          <div class="kpi-label">Root Causes ID'd</div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon confidence">
          <el-icon><Medal /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ avgConfidence }}%</div>
          <div class="kpi-label">Avg Confidence</div>
        </div>
      </div>
    </div>

    <!-- RCA Results - Main Analysis Table -->
    <div class="results-card">
      <div class="card-header">
        <h3>Root Cause Analysis Results</h3>
        <div class="filter-group">
          <select v-model="filters.severity" class="filter-select">
            <option value="all">All Severities</option>
            <option value="critical">Critical</option>
            <option value="major">Major</option>
            <option value="minor">Minor</option>
          </select>
          <select v-model="filters.status" class="filter-select">
            <option value="all">All Status</option>
            <option value="pending">Pending</option>
            <option value="analyzed">Analyzed</option>
            <option value="verified">Verified</option>
          </select>
          <input type="text" v-model="filters.search" placeholder="Search faults..." class="search-input" />
        </div>
      </div>

      <el-table :data="paginatedFaults" stripe v-loading="tableLoading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" label="Fault Title"  show-overflow-tooltip />
        <el-table-column prop="category" label="Category" >
          <template #default="{ row }">
            <el-tag size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="severity" label="Severity" >
          <template #default="{ row }">
            <el-tag :type="getSeverityTagType(row.severity)" size="small" effect="dark">
              {{ row.severity.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="rootCause" label="Root Cause" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.rootCause" class="root-cause-text">{{ row.rootCause }}</span>
            <span v-else class="text-muted">— Pending Analysis —</span>
          </template>
        </el-table-column>
        <el-table-column prop="confidence" label="Confidence"  align="center">
          <template #default="{ row }">
            <div v-if="row.confidence" class="confidence-cell">
              <el-progress :percentage="row.confidence" :stroke-width="8" :show-text="true" :color="getConfidenceColor(row.confidence)" />
            </div>
            <span v-else class="text-muted">—</span>
          </template>
        </el-table-column>
        <el-table-column prop="matchedRule" label="Matched Rule">
          <template #default="{ row }">
            <span v-if="row.matchedRule" class="rule-tag">{{ row.matchedRule }}</span>
            <span v-else class="text-muted">—</span>
          </template>
        </el-table-column>
        <el-table-column label="Actions"  fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDetails(row)">Details</el-button>
            <el-button link type="success" size="small" @click="verifyRCA(row)" :disabled="!row.rootCause">Verify</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredFaults.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Rule Engine Explanation -->
    <div class="rules-card">
      <div class="card-header">
        <h3>Rule Engine</h3>
        <el-button link type="primary" @click="showAllRules = !showAllRules">
          {{ showAllRules ? 'Hide Rules' : 'View All Rules' }}
        </el-button>
      </div>
      <div class="rules-summary">
        <div class="rule-stat">
          <span class="stat-value">{{ rules.length }}</span>
          <span class="stat-label">Active Rules</span>
        </div>
        <div class="rule-stat">
          <span class="stat-value">{{ rules.filter(r => r.triggerCount).reduce((sum, r) => sum + (r.triggerCount || 0), 0) }}</span>
          <span class="stat-label">Total Triggers</span>
        </div>
        <div class="rule-stat">
          <span class="stat-value">{{ (matchRate * 100).toFixed(1) }}%</span>
          <span class="stat-label">Match Rate</span>
        </div>
      </div>
      <div class="rules-list" v-if="showAllRules">
        <div v-for="rule in rules" :key="rule.id" class="rule-item">
          <div class="rule-header">
            <div class="rule-name">{{ rule.name }}</div>
            <div class="rule-priority" :class="getPriorityClass(rule.priority)">
              {{ rule.priority }}
            </div>
          </div>
          <div class="rule-condition">IF: {{ rule.condition }}</div>
          <div class="rule-conclusion">THEN: {{ rule.conclusion }}</div>
          <div class="rule-meta">
            <span>Confidence: {{ rule.confidence }}%</span>
            <span>Triggered: {{ rule.triggerCount || 0 }} times</span>
            <span>Last used: {{ rule.lastUsed || 'Never' }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Rule Manager Dialog -->
    <el-dialog v-model="ruleManagerVisible" title="Rule Manager" width="700px">
      <div class="rule-manager">
        <div class="rule-manager-header">
          <el-button type="primary" size="small" @click="addNewRule">
            <el-icon><Plus /></el-icon> Add Rule
          </el-button>
          <el-input v-model="ruleSearch" placeholder="Search rules..." :prefix-icon="Search" style="width: 200px" />
        </div>
        <el-table :data="filteredRules" stripe size="small" style="margin-top: 16px">
          <el-table-column prop="name" label="Rule Name" min-width="160" />
          <el-table-column prop="condition" label="Condition" min-width="200" show-overflow-tooltip />
          <el-table-column prop="conclusion" label="Conclusion" min-width="160" show-overflow-tooltip />
          <el-table-column prop="priority" label="Priority" width="80">
            <template #default="{ row }">
              <el-tag :type="getPriorityTagType(row.priority)" size="small">{{ row.priority }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="confidence" label="Confidence" width="100">
            <template #default="{ row }">
              <el-progress :percentage="row.confidence" :stroke-width="6" :show-text="true" />
            </template>
          </el-table-column>
          <el-table-column label="Actions" width="100">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="editRule(row)">Edit</el-button>
              <el-button link type="danger" size="small" @click="deleteRule(row)">Delete</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

    <!-- Fault Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" title="RCA Analysis Details" width="650px">
      <div class="detail-content" v-if="selectedFault">
        <div class="detail-section">
          <div class="detail-title">Fault Information</div>
          <div class="detail-grid">
            <div class="detail-item"><span class="label">ID:</span> #{{ selectedFault.id }}</div>
            <div class="detail-item"><span class="label">Title:</span> {{ selectedFault.title }}</div>
            <div class="detail-item"><span class="label">Category:</span> {{ selectedFault.category }}</div>
            <div class="detail-item"><span class="label">Severity:</span>
              <el-tag :type="getSeverityTagType(selectedFault.severity)" size="small">{{ selectedFault.severity }}</el-tag>
            </div>
            <div class="detail-item"><span class="label">Asset:</span> {{ selectedFault.asset }}</div>
            <div class="detail-item"><span class="label">Location:</span> {{ selectedFault.location }}</div>
            <div class="detail-item"><span class="label">Detected:</span> {{ selectedFault.detectedAt }}</div>
          </div>
        </div>

        <div class="detail-section">
          <div class="detail-title">Root Cause Analysis</div>
          <div class="detail-item"><span class="label">Root Cause:</span> {{ selectedFault.rootCause || 'Analysis pending' }}</div>
          <div class="detail-item"><span class="label">Confidence:</span>
            <el-progress :percentage="selectedFault.confidence || 0" :stroke-width="8" :show-text="true" style="width: 200px" />
          </div>
          <div class="detail-item"><span class="label">Matched Rule:</span> {{ selectedFault.matchedRule || '—' }}</div>
        </div>

        <div class="detail-section" v-if="selectedFault.evidence">
          <div class="detail-title">Supporting Evidence</div>
          <ul class="evidence-list">
            <li v-for="ev in selectedFault.evidence" :key="ev">{{ ev }}</li>
          </ul>
        </div>

        <div class="detail-section" v-if="selectedFault.recommendations">
          <div class="detail-title">Recommended Actions</div>
          <ul class="action-list">
            <li v-for="act in selectedFault.recommendations" :key="act">{{ act }}</li>
          </ul>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="verifyRCA(selectedFault)" v-if="selectedFault?.rootCause">Verify RCA</el-button>
      </template>
    </el-dialog>

    <!-- Add/Edit Rule Dialog -->
    <el-dialog v-model="ruleFormVisible" :title="editingRule ? 'Edit Rule' : 'Add New Rule'" width="550px">
      <el-form :model="ruleForm" label-width="100px">
        <el-form-item label="Rule Name" required>
          <el-input v-model="ruleForm.name" placeholder="e.g., Chiller High Pressure Rule" />
        </el-form-item>
        <el-form-item label="Condition" required>
          <el-input type="textarea" v-model="ruleForm.condition" rows="2" placeholder="IF condition description..." />
        </el-form-item>
        <el-form-item label="Conclusion" required>
          <el-input type="textarea" v-model="ruleForm.conclusion" rows="2" placeholder="THEN root cause conclusion..." />
        </el-form-item>
        <el-form-item label="Priority">
          <el-select v-model="ruleForm.priority">
            <el-option label="High" value="high" />
            <el-option label="Medium" value="medium" />
            <el-option label="Low" value="low" />
          </el-select>
        </el-form-item>
        <el-form-item label="Confidence">
          <el-slider v-model="ruleForm.confidence" :min="50" :max="100" :step="5" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="ruleFormVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveRule">Save Rule</el-button>
      </template>
    </el-dialog>

    <!-- Analysis Running Toast -->
    <div v-if="analysisRunning" class="analysis-toast">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>Running RCA analysis on {{ filteredFaults.length }} faults...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  Refresh, Download, WarningFilled, DocumentChecked, Position, Medal,
  TrendCharts, Setting, Plus, Search, Loading
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading State
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const tableLoading = ref(false)
const analysisRunning = ref(false)
const loadingMessages = ['Preparing...', 'Loading rule engine...', 'Initializing knowledge base...', 'Almost ready...']

// Data Models
interface Fault {
  id: number
  title: string
  category: string
  severity: 'critical' | 'major' | 'minor'
  asset: string
  location: string
  detectedAt: string
  status: 'pending' | 'analyzed' | 'verified'
  rootCause?: string
  confidence?: number
  matchedRule?: string
  evidence?: string[]
  recommendations?: string[]
  symptoms?: string[]
}

interface Rule {
  id: number
  name: string
  condition: string
  conclusion: string
  priority: 'high' | 'medium' | 'low'
  confidence: number
  triggerCount?: number
  lastUsed?: string
  category?: string[]
  symptoms?: string[]
}

// State
const filters = ref({
  severity: 'all',
  status: 'all',
  search: ''
})
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)
const ruleManagerVisible = ref(false)
const ruleFormVisible = ref(false)
const showAllRules = ref(true)
const ruleSearch = ref('')
const editingRule = ref<Rule | null>(null)
const selectedFault = ref<Fault | null>(null)

// Mock Data - Faults
const faults = ref<Fault[]>([
  { id: 1001, title: 'Chiller-02 High Pressure Trip', category: 'HVAC', severity: 'critical', asset: 'Chiller-02', location: 'Building A - Plant Room', detectedAt: '2025-05-29 08:23:15', status: 'analyzed', rootCause: 'Condenser water flow reduced due to cooling tower fan failure', confidence: 94, matchedRule: 'R-101: Chiller High Pressure Rule', evidence: ['Cooling tower fan status: OFF', 'Condenser water flow: 45% below normal', 'Chiller approach temperature: +3.5°C'], recommendations: ['Restore cooling tower fan operation', 'Inspect condenser water pump', 'Reset chiller after flow restoration'] },
  { id: 1002, title: 'UPS-01 Input Power Loss', category: 'Electrical', severity: 'critical', asset: 'UPS-01', location: 'Data Center - UPS Room', detectedAt: '2025-05-29 07:45:22', status: 'analyzed', rootCause: 'Main switchboard breaker tripped due to downstream fault', confidence: 92, matchedRule: 'R-201: UPS Power Loss Rule', evidence: ['Breaker status: OPEN', 'Downstream PDU: Overload alarm', 'Input voltage: 0V'], recommendations: ['Check main breaker status', 'Isolate downstream loads', 'Close breaker and monitor'] },
  { id: 1003, title: 'Server Room Temperature High', category: 'DCIM', severity: 'critical', asset: 'CRAC-03', location: 'Data Center - Row A', detectedAt: '2025-05-29 06:30:05', status: 'analyzed', rootCause: 'CRAC-03 compressor failure', confidence: 96, matchedRule: 'R-301: High Temperature Rule', evidence: ['CRAC-03 status: FAULT', 'Compressor current: 0A', 'Supply air temperature: 24°C vs setpoint 18°C'], recommendations: ['Check CRAC compressor', 'Verify refrigerant charge', 'Consider temporary cooling'] },
  { id: 1004, title: 'AHU-201 Filter Clogged', category: 'HVAC', severity: 'major', asset: 'AHU-201', location: 'Building B - Mechanical Room', detectedAt: '2025-05-28 22:15:30', status: 'analyzed', rootCause: 'Filter maintenance overdue - 90 days since last change', confidence: 88, matchedRule: 'R-102: AHU Filter Clog Rule', evidence: ['Differential pressure: 180Pa (normal: 80Pa)', 'Last filter change: 90 days ago', 'Airflow: 25% below setpoint'], recommendations: ['Replace AHU filters', 'Reset differential pressure sensor', 'Update maintenance schedule'] },
  { id: 1005, title: 'VFD-105 Overcurrent Fault', category: 'Electrical', severity: 'major', asset: 'VFD-105', location: 'Building A - Electrical Room', detectedAt: '2025-05-28 14:20:10', status: 'pending', rootCause: undefined, confidence: undefined, matchedRule: undefined },
  { id: 1006, title: 'Water Leak Detected', category: 'Plumbing', severity: 'major', asset: 'LL-103', location: 'Building A - Basement', detectedAt: '2025-05-28 11:35:42', status: 'analyzed', rootCause: 'Pump seal failure causing water seepage', confidence: 85, matchedRule: 'R-501: Water Leak Rule', evidence: ['Leak sensor: WET', 'Humidity: 75% (normal: 50%)', 'Pump vibration: +0.3mm/s'], recommendations: ['Isolate water supply', 'Replace pump seal', 'Dry affected area'] },
  { id: 1007, title: 'Fire Alarm Panel Fault', category: 'Fire Safety', severity: 'critical', asset: 'FA-101', location: 'Building A - Fire Command', detectedAt: '2025-05-27 23:10:15', status: 'pending', rootCause: undefined, confidence: undefined, matchedRule: undefined },
  { id: 1008, title: 'FCU-205 Not Responding', category: 'HVAC', severity: 'major', asset: 'FCU-205', location: 'Building B - Floor 2', detectedAt: '2025-05-27 15:20:00', status: 'analyzed', rootCause: 'FCU controller communication loss', confidence: 82, matchedRule: 'R-103: FCU Communication Rule', evidence: ['FCU status: OFFLINE', 'BACnet communication: TIMEOUT', 'Neighbor devices: ONLINE'], recommendations: ['Check FCU power supply', 'Verify BACnet wiring', 'Reset FCU controller'] },
  { id: 1009, title: 'Generator Fuel Low', category: 'Electrical', severity: 'critical', asset: 'GEN-01', location: 'Building B - Generator Room', detectedAt: '2025-05-27 11:00:00', status: 'pending', rootCause: undefined, confidence: undefined, matchedRule: undefined },
  { id: 1010, title: 'BMS Gateway Offline', category: 'BMS', severity: 'major', asset: 'BMS-GW-01', location: 'Building B - BMS Room', detectedAt: '2025-05-26 20:30:00', status: 'analyzed', rootCause: 'Network switch port failure', confidence: 90, matchedRule: 'R-601: BMS Gateway Rule', evidence: ['Gateway ping: FAILED', 'Switch port status: DOWN', 'Power status: OK'], recommendations: ['Check network switch', 'Verify port configuration', 'Restart gateway'] }
])

// Mock Data - Rules
const rules = ref<Rule[]>([
  { id: 101, name: 'R-101: Chiller High Pressure Rule', condition: 'Chiller high pressure alarm AND cooling tower fan status = OFF AND condenser water flow < 50%', conclusion: 'Condenser water flow reduced due to cooling tower fan failure', priority: 'high', confidence: 94, triggerCount: 12, lastUsed: '2025-05-29 08:23:15', category: ['HVAC'], symptoms: ['High pressure alarm', 'Reduced cooling capacity'] },
  { id: 102, name: 'R-102: AHU Filter Clog Rule', condition: 'AHU differential pressure > 150Pa AND airflow < 80% setpoint AND last filter change > 60 days', conclusion: 'Filter maintenance overdue causing reduced airflow', priority: 'high', confidence: 88, triggerCount: 8, lastUsed: '2025-05-28 22:15:30', category: ['HVAC'], symptoms: ['Low airflow', 'High static pressure'] },
  { id: 103, name: 'R-103: FCU Communication Rule', condition: 'FCU status = OFFLINE AND BACnet communication timeout AND neighboring devices online', conclusion: 'FCU controller communication loss due to network or power issue', priority: 'medium', confidence: 82, triggerCount: 5, lastUsed: '2025-05-27 15:20:00', category: ['HVAC', 'BMS'], symptoms: ['Device offline', 'Communication error'] },
  { id: 201, name: 'R-201: UPS Power Loss Rule', condition: 'UPS input voltage = 0 AND main breaker status = OPEN AND downstream PDU overload', conclusion: 'Main switchboard breaker tripped due to downstream fault', priority: 'high', confidence: 92, triggerCount: 6, lastUsed: '2025-05-29 07:45:22', category: ['Electrical'], symptoms: ['Power loss', 'Breaker trip'] },
  { id: 301, name: 'R-301: High Temperature Rule', condition: 'Room temperature > 28°C AND CRAC status = FAULT AND compressor current = 0', conclusion: 'CRAC compressor failure causing temperature rise', priority: 'high', confidence: 96, triggerCount: 4, lastUsed: '2025-05-29 06:30:05', category: ['DCIM'], symptoms: ['High temperature', 'Cooling failure'] },
  { id: 501, name: 'R-501: Water Leak Rule', condition: 'Leak sensor = WET AND humidity > 70% AND pump vibration > 0.2mm/s', conclusion: 'Pump seal failure causing water leakage', priority: 'medium', confidence: 85, triggerCount: 3, lastUsed: '2025-05-28 11:35:42', category: ['Plumbing'], symptoms: ['Water leak', 'High humidity'] },
  { id: 601, name: 'R-601: BMS Gateway Rule', condition: 'Gateway ping FAILED AND switch port DOWN AND power status OK', conclusion: 'Network switch port failure causing gateway offline', priority: 'medium', confidence: 90, triggerCount: 7, lastUsed: '2025-05-26 20:30:00', category: ['BMS'], symptoms: ['Gateway offline', 'Communication lost'] }
])

// Computed
const totalFaults = computed(() => faults.value.length)
const analyzedCount = computed(() => faults.value.filter(f => f.status === 'analyzed' || f.status === 'verified').length)
const rootCauseIdentified = computed(() => faults.value.filter(f => f.rootCause).length)
const avgConfidence = computed(() => {
  const withConfidence = faults.value.filter(f => f.confidence)
  if (withConfidence.length === 0) return 0
  return Math.round(withConfidence.reduce((sum, f) => sum + (f.confidence || 0), 0) / withConfidence.length)
})
const matchRate = computed(() => analyzedCount.value / totalFaults.value)

const filteredFaults = computed(() => {
  let result = [...faults.value]
  if (filters.value.severity !== 'all') {
    result = result.filter(f => f.severity === filters.value.severity)
  }
  if (filters.value.status !== 'all') {
    result = result.filter(f => f.status === filters.value.status)
  }
  if (filters.value.search) {
    const search = filters.value.search.toLowerCase()
    result = result.filter(f =>
        f.title.toLowerCase().includes(search) ||
        f.asset.toLowerCase().includes(search) ||
        f.category.toLowerCase().includes(search)
    )
  }
  return result
})

const paginatedFaults = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredFaults.value.slice(start, end)
})

const filteredRules = computed(() => {
  if (!ruleSearch.value) return rules.value
  const search = ruleSearch.value.toLowerCase()
  return rules.value.filter(r =>
      r.name.toLowerCase().includes(search) ||
      r.condition.toLowerCase().includes(search) ||
      r.conclusion.toLowerCase().includes(search)
  )
})

// Helper Functions
const getSeverityTagType = (severity: string) => {
  const map: Record<string, string> = { critical: 'danger', major: 'warning', minor: 'info' }
  return map[severity] || 'info'
}

const getConfidenceColor = (confidence: number) => {
  if (confidence >= 90) return '#67c23a'
  if (confidence >= 80) return '#409eff'
  if (confidence >= 70) return '#e6a23c'
  return '#f56c6c'
}

const getPriorityClass = (priority: string) => {
  const map: Record<string, string> = { high: 'priority-high', medium: 'priority-medium', low: 'priority-low' }
  return map[priority] || ''
}

const getPriorityTagType = (priority: string) => {
  const map: Record<string, string> = { high: 'danger', medium: 'warning', low: 'info' }
  return map[priority] || 'info'
}

// Actions
const runAnalysis = async () => {
  analysisRunning.value = true
  tableLoading.value = true

  // Simulate RCA engine processing
  await new Promise(resolve => setTimeout(resolve, 2000))

  // Process pending faults
  faults.value.forEach(fault => {
    if (fault.status === 'pending') {
      // Simple rule matching simulation
      if (fault.title.includes('Chiller') || fault.title.includes('Chiller')) {
        fault.rootCause = 'Condenser water flow reduced due to cooling tower fan failure'
        fault.confidence = 94
        fault.matchedRule = 'R-101: Chiller High Pressure Rule'
        fault.status = 'analyzed'
        fault.evidence = ['Cooling tower fan status: OFF', 'Condenser water flow: 45% below normal']
        fault.recommendations = ['Restore cooling tower fan operation', 'Reset chiller']
      } else if (fault.title.includes('Fire')) {
        fault.rootCause = 'Zone 3 smoke detector contamination causing false alarm'
        fault.confidence = 87
        fault.matchedRule = 'R-701: Fire Alarm Rule'
        fault.status = 'analyzed'
        fault.evidence = ['Detector status: ALARM', 'No heat signature detected']
        fault.recommendations = ['Inspect detector sensor', 'Clean or replace detector']
      } else if (fault.title.includes('Generator')) {
        fault.rootCause = 'Fuel delivery schedule missed - tank below minimum level'
        fault.confidence = 92
        fault.matchedRule = 'R-202: Generator Fuel Rule'
        fault.status = 'analyzed'
        fault.evidence = ['Fuel level: 12% (minimum: 25%)', 'Last delivery: 45 days ago']
        fault.recommendations = ['Schedule emergency fuel delivery', 'Review fuel monitoring schedule']
      }
    }
  })

  ElMessage.success(`RCA analysis complete: ${filteredFaults.value.filter(f => f.status === 'analyzed').length} faults analyzed`)
  analysisRunning.value = false
  tableLoading.value = false
}

const viewDetails = (fault: Fault) => {
  selectedFault.value = fault
  detailDialogVisible.value = true
}

const verifyRCA = (fault: Fault) => {
  if (!fault) return
  fault.status = 'verified'
  ElMessage.success(`RCA verified for fault #${fault.id}`)
  detailDialogVisible.value = false
}

const refreshData = () => {
  ElMessage.success('Data refreshed')
}

const openRuleManager = () => {
  ruleManagerVisible.value = true
  ruleSearch.value = ''
}

const addNewRule = () => {
  editingRule.value = null
  ruleForm.value = {
    name: '',
    condition: '',
    conclusion: '',
    priority: 'medium',
    confidence: 85
  }
  ruleFormVisible.value = true
}

const editRule = (rule: Rule) => {
  editingRule.value = rule
  ruleForm.value = {
    name: rule.name,
    condition: rule.condition,
    conclusion: rule.conclusion,
    priority: rule.priority,
    confidence: rule.confidence
  }
  ruleFormVisible.value = true
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

const ruleForm = ref({
  name: '',
  condition: '',
  conclusion: '',
  priority: 'medium' as 'high' | 'medium' | 'low',
  confidence: 85
})

const saveRule = () => {
  if (!ruleForm.value.name || !ruleForm.value.condition || !ruleForm.value.conclusion) {
    ElMessage.warning('Please fill all required fields')
    return
  }

  if (editingRule.value) {
    // Update existing rule
    const index = rules.value.findIndex(r => r.id === editingRule.value!.id)
    if (index !== -1) {
      rules.value[index] = {
        ...rules.value[index],
        name: ruleForm.value.name,
        condition: ruleForm.value.condition,
        conclusion: ruleForm.value.conclusion,
        priority: ruleForm.value.priority,
        confidence: ruleForm.value.confidence
      }
      ElMessage.success('Rule updated')
    }
  } else {
    // Add new rule
    const newId = Math.max(...rules.value.map(r => r.id), 0) + 1
    rules.value.push({
      id: newId,
      name: ruleForm.value.name,
      condition: ruleForm.value.condition,
      conclusion: ruleForm.value.conclusion,
      priority: ruleForm.value.priority,
      confidence: ruleForm.value.confidence,
      triggerCount: 0
    })
    ElMessage.success('Rule added')
  }
  ruleFormVisible.value = false
  editingRule.value = null
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
    setTimeout(() => { isLoaded.value = true }, 400)
  }, 2000)
})
</script>

<style scoped>
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
.rca-page {
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
.kpi-icon.total { background: #fee2e2; color: #dc2626; }
.kpi-icon.analyzed { background: #e8f4ff; color: #3b82f6; }
.kpi-icon.identified { background: #fef3c7; color: #d97706; }
.kpi-icon.confidence { background: #d1fae5; color: #059669; }
.kpi-info { flex: 1; }
.kpi-value { font-size: 28px; font-weight: 700; color: #1a1a2e; }
.kpi-label { font-size: 13px; color: #64748b; margin-top: 4px; }

/* Results Card */
.results-card, .rules-card {
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
.filter-group {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
.filter-select, .search-input {
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 13px;
  background: white;
}
.search-input { width: 200px; }

.root-cause-text {
  color: #10b981;
  font-weight: 500;
}
.rule-tag {
  background: #dbeafe;
  color: #1d4ed8;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
}
.text-muted {
  color: #c0c4cc;
  font-style: italic;
}
.confidence-cell {
  width: 100%;
}
.pagination-wrapper {
  padding-top: 16px;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #e2e8f0;
  margin-top: 16px;
}

/* Rules Card */
.rules-summary {
  display: flex;
  gap: 32px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
}
.rule-stat {
  text-align: center;
}
.rule-stat .stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a2e;
  display: block;
}
.rule-stat .stat-label {
  font-size: 12px;
  color: #64748b;
}
.rules-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 400px;
  overflow-y: auto;
}
.rule-item {
  background: #f8fafc;
  border-radius: 12px;
  padding: 14px;
  border-left: 4px solid #cbd5e1;
}
.rule-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.rule-name {
  font-weight: 600;
  color: #1a1a2e;
}
.rule-priority {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 12px;
  font-weight: 600;
}
.rule-priority.priority-high { background: #fee2e2; color: #dc2626; }
.rule-priority.priority-medium { background: #fef3c7; color: #d97706; }
.rule-priority.priority-low { background: #dbeafe; color: #2563eb; }
.rule-condition, .rule-conclusion {
  font-size: 12px;
  color: #475569;
  margin-bottom: 6px;
}
.rule-condition:before { content: "📋 "; }
.rule-conclusion:before { content: "✅ "; }
.rule-meta {
  display: flex;
  gap: 16px;
  margin-top: 8px;
  font-size: 10px;
  color: #94a3b8;
}

/* Dialog Styles */
.detail-content { padding: 8px 0; }
.detail-section {
  margin-bottom: 24px;
}
.detail-title {
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 12px;
  font-size: 15px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e2e8f0;
}
.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}
.detail-item {
  font-size: 13px;
}
.detail-item .label {
  color: #64748b;
  margin-right: 8px;
}
.evidence-list, .action-list {
  margin: 8px 0 0 20px;
  padding: 0;
}
.evidence-list li, .action-list li {
  font-size: 13px;
  color: #475569;
  margin-bottom: 6px;
}

.rule-manager-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.analysis-toast {
  position: fixed;
  bottom: 30px;
  right: 30px;
  background: #1e293b;
  color: white;
  padding: 12px 20px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 1000;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

:deep(.el-table) { border-radius: 12px; }
:deep(.el-table th) { background-color: #fafafa; font-weight: 600; }
:deep(.el-progress__text) { font-size: 11px !important; }
</style>